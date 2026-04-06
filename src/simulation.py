import math
import random
import numpy as np

import src.obj as obj
import src.config as config

configuration = config.parse_config("./simulation.config")

MOOD_AMAZING = int(configuration["mood_amazing"])
MOOD_EXCITED = int(configuration["mood_excited"])
MOOD_HAPPY = int(configuration["mood_happy"])
MOOD_CONTENT = int(configuration["mood_content"])
MOOD_SAD = int(configuration["mood_sad"])
MOOD_IRRITATED = int(configuration["mood_irritated"])
MOOD_ANGRY = int(configuration["mood_angry"])
MOOD_FURY = int(configuration["mood_fury"])

MOOD_MIN_START = int(configuration["mood_min_start"])
MOOD_RADIUS = float(configuration["mood_radius"])

PEEP_MOVE_SPEED = float(configuration["peep_move_speed"])
PEEP_SPAWN_RADIUS = float(configuration["peep_spawn_radius"])
PEEP_BOUND_BOX = float(configuration["peep_bound_box"])
PEEP_SPREAD_DISTANCE = float(configuration["peep_spread_distance"])

EVENT_ROLL_INTERVAL = int(configuration["event_roll_interval"])
EVENT_ROLL_CHANCE = int(configuration["event_roll_chance"])
EVENT_DURATION_MIN = int(configuration["event_duration_min"])
EVENT_DURATION_MAX = int(configuration["event_duration_max"])
EVENT_ACTOR_RADIUS = float(configuration["event_actor_radius"])
EVENT_ACTOR_POWER = float(configuration["event_actor_power"])
EVENT_ACTOR_MOVE_SPEED = float(configuration["event_actor_move_speed"])

DEFAULT_KFC_COLOR = (242, 50, 66)
DEFAULT_CHURCH_COLOR = (242, 245, 66)
CLOSED_BUILDING_COLOR = (120, 120, 120)
DEVIL_CHURCH_COLOR = (190, 35, 35)

KFC_POSITION = [0.0, 0.0, 6.0]
CHURCH_POSITION = [-6.0, 0.0, -7.0]

# Which genius decided python didnt need enums??

EVENT_NONE = "none"
EVENT_KFC_CLOSED = "kfc closed"
EVENT_CHURCH_CLOSED = "church closed"
EVENT_GOD_RISEN = "god has risen"
EVENT_DEVIL_RISEN = "devil has risen"
EVENT_PURGE = "the purge"

peeps = []

current_event = EVENT_NONE
event_ticks_left = 0
event_roll_ticks = EVENT_ROLL_INTERVAL
event_actor = None


# Clamps a value within a range.
def clamp(value, min_value=0.0, max_value=100.0):
    return max(min_value, min(max_value, value))


# Clamp a point so it stays within floor bounds.
def clamp_ground_point(point):
    return [
        clamp(point[0], -PEEP_BOUND_BOX, PEEP_BOUND_BOX),
        0.0,
        clamp(point[2], -PEEP_BOUND_BOX, PEEP_BOUND_BOX),
    ]


# Measure the distance between two points.
def distance_between(vec1, vec2):
    return float(np.linalg.norm(np.array(vec2) - np.array(vec1)))


# Pick a random point inside a radius.
def random_ground_point(radius):
    angle = random.uniform(0.0, math.tau)
    size = radius * math.sqrt(random.random())
    return [size * math.cos(angle), 0.0, size * math.sin(angle)]


# Pick a random ground point near an origin.
# The sqrt function is required to spread out peeps.
def random_point_near(origin, radius):
    angle = random.uniform(0.0, math.tau)
    size = radius * math.sqrt(random.random())
    point = [
        origin[0] + (size * math.cos(angle)),
        0.0,
        origin[2] + (size * math.sin(angle)),
    ]
    return clamp_ground_point(point)


# Pick a random point anywhere inside the map bounds.
def random_wander_point():
    return [
        random.uniform(-PEEP_BOUND_BOX, PEEP_BOUND_BOX),
        0.0,
        random.uniform(-PEEP_BOUND_BOX, PEEP_BOUND_BOX),
    ]


# Normalised vector from one point to another.
def direction_vector(start, finish):
    vector = np.array(finish) - np.array(start)
    length = np.linalg.norm(vector)
    if length == 0:
        angle = random.uniform(0.0, math.tau)
        return np.array([math.cos(angle), 0.0, math.sin(angle)])
    return vector / length


# Find a point that moves away from Actor.
def point_away_from(source, actor, distance):
    direction = direction_vector(actor, source)
    point = np.array(source) + (direction * distance)
    return clamp_ground_point([point[0], 0.0, point[2]])


# Find the nearest peep in a nearby list.
def closest_nearby_peep(nearby_peeps):
    if len(nearby_peeps) == 0:
        return None, 0.0

    closest_peep = nearby_peeps[0][0]
    closest_distance = nearby_peeps[0][1]

    for peep_data in nearby_peeps[1:]:
        peep = peep_data[0]
        distance = peep_data[1]
        if distance < closest_distance:
            closest_peep = peep
            closest_distance = distance

    return closest_peep, closest_distance


# Find the peep closest to a world position.
def closest_peep_to_position(position):
    closest = None
    closest_distance = 0.0

    for peep in peeps:
        distance = distance_between(position, peep.position)
        if closest is None or distance < closest_distance:
            closest = peep
            closest_distance = distance

    return closest, closest_distance


# Update world settings after the scene is loaded.
def configure_world(
    church_position=None,
    kfc_position=None,
    move_speed=None,
    spawn_radius=None,
    bound_box=None,
):
    # Assment outline advices against globals but its sensible for this
    global CHURCH_POSITION, KFC_POSITION, PEEP_MOVE_SPEED, PEEP_SPAWN_RADIUS, PEEP_BOUND_BOX

    if church_position is not None:
        CHURCH_POSITION = [
            float(church_position[0]),
            0.0,
            float(church_position[2]),
        ]
    if kfc_position is not None:
        KFC_POSITION = [
            float(kfc_position[0]),
            0.0,
            float(kfc_position[2]),
        ]
    if move_speed is not None:
        PEEP_MOVE_SPEED = float(move_speed)
    if spawn_radius is not None:
        PEEP_SPAWN_RADIUS = float(spawn_radius)
    if bound_box is not None:
        PEEP_BOUND_BOX = float(bound_box)


# Actors like the devil and god.
class Actor:
    # Default Values
    def __init__(self, color, influence_kind, start_position):
        self.mesh = obj.load("./meshes/peep.obj")
        self.mesh.color = color
        self.mesh.transform.scale = [1.8, 1.8, 1.8]
        self.position = [start_position[0], 0.0, start_position[2]]
        self.influence_kind = influence_kind
        self.move_speed = EVENT_ACTOR_MOVE_SPEED
        self.movement_actions = []
        self.chase_refresh = 0
        self.transfer_movement()

    # Copy the actor position into its mesh transform.
    def transfer_movement(self):
        self.mesh.transform.translate[0] = self.position[0]
        self.mesh.transform.translate[1] = self.position[1]
        self.mesh.transform.translate[2] = self.position[2]
        self.mesh.transform.update_model()

    # Queue movement steps toward a point.
    def move_to(self, point):
        start = self.position
        if len(self.movement_actions) != 0:
            start = self.movement_actions[-1]
        self.movement_actions = lerp_vector3(start, point, self.move_speed)

    # Move the actor forward by one step.
    def step_movement(self):
        if len(self.movement_actions) == 0:
            return

        self.position = self.movement_actions[0]
        self.movement_actions.pop(0)
        self.transfer_movement()

    # Run one tick of actor behaviour.
    def tick(self):
        self.step_movement()

        if self.influence_kind == "god":
            if len(self.movement_actions) == 0:
                self.move_to(random_point_near(CHURCH_POSITION, 3.0))
            for peep in peeps:
                distance = distance_between(self.position, peep.position)
                if distance > EVENT_ACTOR_RADIUS:
                    continue
                influence = 1.0 - (distance / EVENT_ACTOR_RADIUS)
                peep.social = clamp(
                    peep.social + ((EVENT_ACTOR_POWER * 2.5) * influence)
                )
                peep.religion = clamp(
                    peep.religion + ((EVENT_ACTOR_POWER * 5.0) * influence)
                )
                peep.hunger = clamp(
                    peep.hunger + ((EVENT_ACTOR_POWER * 1.2) * influence)
                )
                peep.church_urge += 0.35 * influence
            return

        if self.chase_refresh > 0:
            self.chase_refresh -= 1
        if len(self.movement_actions) == 0 or self.chase_refresh == 0:
            target, _ = closest_peep_to_position(self.position)
            if target is None:
                self.move_to(random_wander_point())
            else:
                self.move_to(target.position)
            self.chase_refresh = 7

        for peep in peeps:
            distance = distance_between(self.position, peep.position)
            if distance > EVENT_ACTOR_RADIUS:
                continue
            influence = 1.0 - (distance / EVENT_ACTOR_RADIUS)
            peep.social = clamp(peep.social - ((EVENT_ACTOR_POWER * 3.0) * influence))
            peep.religion = clamp(
                peep.religion - ((EVENT_ACTOR_POWER * 5.0) * influence)
            )
            peep.hunger = clamp(peep.hunger - ((EVENT_ACTOR_POWER * 1.5) * influence))
            peep.wealth = clamp(peep.wealth - ((EVENT_ACTOR_POWER * 0.8) * influence))


# Calculate the current average mood of all peeps.
def average_happiness():
    if len(peeps) == 0:
        return 0.0

    total_mood = 0.0
    for peep in peeps:
        total_mood += peep.mood
    return total_mood / float(len(peeps))


# Start an event.
def start_event(name):
    global current_event, event_ticks_left, event_actor

    current_event = name
    event_ticks_left = random.randint(EVENT_DURATION_MIN, EVENT_DURATION_MAX)
    event_actor = None

    if name == EVENT_GOD_RISEN:
        event_actor = Actor(
            (255, 215, 0), "god", random_point_near(CHURCH_POSITION, 1.5)
        )
        # Give everyone a bunch of money to fix that money issue
        for peep in peeps:
            peep.wealth = clamp(peep.wealth + 30.0)

    elif name == EVENT_DEVIL_RISEN:
        event_actor = Actor((220, 30, 30), "devil", random_wander_point())
    elif name == EVENT_PURGE:
        for peep in peeps:
            peep.social = clamp(peep.social - 35.0)


# Clear the active event and reset its timers.
def end_current_event():
    global current_event, event_ticks_left, event_actor, event_roll_ticks

    current_event = EVENT_NONE
    event_ticks_left = 0
    event_actor = None
    event_roll_ticks = EVENT_ROLL_INTERVAL


# Event ticking.
def tick_events():
    global event_ticks_left, event_roll_ticks

    if current_event == EVENT_NONE:
        if event_roll_ticks > 0:
            event_roll_ticks -= 1
            return

        event_roll_ticks = EVENT_ROLL_INTERVAL
        if random.randint(1, 100) <= EVENT_ROLL_CHANCE:
            current = [
                EVENT_KFC_CLOSED,
                EVENT_CHURCH_CLOSED,
                EVENT_GOD_RISEN,
                EVENT_DEVIL_RISEN,
                EVENT_PURGE,
            ]
            start_event(random.choice(current))
        return

    if event_actor is not None:
        event_actor.tick()

    event_ticks_left -= 1
    if event_ticks_left <= 0:
        end_current_event()


class Peep:
    # Default peep with random stats
    def __init__(self):
        self.recovery_rate = random.randrange(7, 10)

        self.hunger = random.randrange(MOOD_MIN_START, 100)
        self.social = random.randrange(MOOD_MIN_START, 100)
        self.religion = random.randrange(MOOD_MIN_START, 100)
        self.wealth = random.randrange(MOOD_MIN_START, 100)

        self.prefrences = [
            float(random.randrange(0, 32)) / 100,
            float(random.randrange(0, 32)) / 100,
            float(random.randrange(0, 32)) / 100,
        ]
        self.prefrences.append(
            1 - self.prefrences[0] - self.prefrences[1] - self.prefrences[2]
        )

        self.mesh = obj.load("./meshes/peep.obj")
        self.position = random_ground_point(PEEP_SPAWN_RADIUS)
        self.movement_actions = []
        self.move_speed = PEEP_MOVE_SPEED
        self.base_move_speed = PEEP_MOVE_SPEED
        self.destination_kind = None
        self.last_destination = None

        self.church_urge = 0.0
        self.aggression_cooldown = 0
        self.kfc_cooldown = random.randrange(0, 140)
        self.church_cooldown = random.randrange(0, 180)
        self.food_bias = random.randrange(0, 20)
        self.church_bias = random.randrange(0, 20)
        self.wander_bias = random.randrange(10, 35)
        self.god_bias = random.randrange(0, 20)
        self.bravery = random.randrange(0, 20)
        self.mood = 0.0

        self.transfer_movement()
        self.calculate_mood()
        self.update_visuals()

        peeps.append(self)

    # Calculate the mood value.
    def calculate_mood(self):
        self.mood = clamp(
            (self.hunger * self.prefrences[0])
            + (self.social * self.prefrences[1])
            + (self.religion * self.prefrences[2])
            + (self.wealth * self.prefrences[3])
        )
        return self.mood

    # Convert mood value into a band.
    def mood_band(self):
        if self.mood >= MOOD_AMAZING:
            return "amazing"
        if self.mood >= MOOD_EXCITED:
            return "excited"
        if self.mood >= MOOD_HAPPY:
            return "happy"
        if self.mood >= MOOD_CONTENT:
            return "content"
        if self.mood >= MOOD_SAD:
            return "sad"
        if self.mood >= MOOD_IRRITATED:
            return "irritated"
        if self.mood >= MOOD_ANGRY:
            return "angry"
        return "fury"

    # List nearby peeps within a radius.
    def get_nearby_peeps(self, radius):
        nearby = []
        for other in peeps:
            if other is self:
                continue

            distance = distance_between(self.position, other.position)
            if distance <= radius:
                nearby.append((other, distance))
        return nearby

    # Apply the passive stat changes and update timers for one tick.
    def apply_passive_changes(self):
        recovery = self.recovery_rate / 450.0

        # To Do: Make these configurable
        # I might make these variable later
        self.hunger = clamp(self.hunger - 0.08)
        self.social = clamp(self.social - 0.025 + (recovery * 0.25))
        self.religion = clamp(self.religion - 0.015 + (recovery * 0.1))
        self.wealth = clamp(self.wealth - 0.008 + (recovery * 0.08))
        self.church_urge = max(0.0, self.church_urge - 0.025)

        # Cooldowns
        # Had to add these to avoid peeps just walking to and from kfc/church
        if self.aggression_cooldown > 0:
            self.aggression_cooldown -= 1
        if self.kfc_cooldown > 0:
            self.kfc_cooldown -= 1
        if self.church_cooldown > 0:
            self.church_cooldown -= 1

    # Apply mood effects to nearby peeps.
    def apply_mood_effects(self, nearby_peeps):
        band = self.mood_band()

        for peep_data in nearby_peeps:
            other = peep_data[0]
            distance = peep_data[1]
            influence = 1.0 - (distance / MOOD_RADIUS)

            if band == "amazing":
                other.social = clamp(other.social + (0.05 * influence))
            elif band == "excited":
                other.church_urge += 0.06 * influence
                other.social = clamp(other.social + (0.01 * influence))
            elif band == "happy":
                other.social = clamp(other.social + (0.03 * influence))
            elif band == "irritated":
                other.social = clamp(other.social - (0.03 * influence))
            elif band == "angry":
                other.religion = clamp(other.religion - (0.04 * influence))
            elif band == "fury":
                other.social = clamp(other.social - (0.02 * influence))

    # Adjust movement speed according to action.
    def update_move_speed(self):
        self.move_speed = self.base_move_speed

        if self.destination_kind == "flee":
            self.move_speed = self.base_move_speed * 1.45
        elif self.mood_band() == "sad":
            self.move_speed = max(self.base_move_speed * 0.5, 0.01)

    # Overwrite the current destination and path.
    def set_destination(self, kind, point):
        self.destination_kind = kind
        self.movement_actions.clear()
        self.move_to(point)

    # Applies the effects of visiting KFC.
    def visit_kfc(self):
        if current_event == EVENT_KFC_CLOSED:
            return

        # Food requires wealth!
        # Right now theres no way to regen wealth which scews the sim up
        # This makes everyone eventualy unhappy
        # To Do: add jobs?
        if self.wealth <= 0:
            return

        # If peep has < 5 dollars, give less benafit
        spend = min(self.wealth, 5.0)
        self.wealth = clamp(self.wealth - spend)
        self.hunger = clamp(self.hunger + (16.0 + spend))
        self.social = clamp(self.social + 1.0)

        self.kfc_cooldown = random.randrange(120, 240)

    # Applies the effects of visiting church.
    def visit_church(self):
        if current_event == EVENT_CHURCH_CLOSED:
            return

        # to do: add some donation system where rich peeps donate to poor ones

        self.religion = clamp(self.religion + 12.0)
        self.social = clamp(self.social + 0.8)
        self.church_urge = 0.0

        self.church_cooldown = random.randrange(180, 320)

    # Handle a peep arriving at its destination.
    def handle_arrival(self):
        if (
            self.destination_kind == "kfc"
            and distance_between(self.position, KFC_POSITION) <= 2.0
        ):
            self.visit_kfc()
            self.last_destination = "kfc"
            self.destination_kind = None
        elif (
            self.destination_kind == "church"
            and distance_between(self.position, CHURCH_POSITION) <= 2.0
        ):
            self.visit_church()
            self.last_destination = "church"
            self.destination_kind = None
        elif (
            self.destination_kind in ("wander", "attack", "flee", "god")
            and len(self.movement_actions) == 0
        ):
            # Reset action
            self.last_destination = self.destination_kind
            self.destination_kind = None

    # Try to attack/rob the closest nearby peep.
    def try_attack(self, nearby_peeps):
        if self.aggression_cooldown > 0 or len(nearby_peeps) == 0:
            return False

        target, distance = closest_nearby_peep(nearby_peeps)
        if target is None or distance > 1.35:
            return False

        stolen_wealth = min(target.wealth, 1.5)
        target.wealth = clamp(target.wealth - stolen_wealth)
        self.wealth = clamp(self.wealth + stolen_wealth)
        target.social = clamp(target.social - 1.5)
        target.hunger = clamp(target.hunger - 0.6)

        self.aggression_cooldown = 80  # to do : add to config!
        self.destination_kind = None
        self.movement_actions.clear()
        return True

    # Choose the next destination based on mood and events.
    def choose_next_action(self, nearby_peeps):
        if current_event == EVENT_DEVIL_RISEN:
            safe_distance = EVENT_ACTOR_RADIUS + 1.5 + ((18 - self.bravery) * 0.15)
            if distance_between(self.position, event_actor.position) < safe_distance:
                flee_target = point_away_from(
                    self.position,
                    event_actor.position,
                    PEEP_SPREAD_DISTANCE + random.uniform(1.0, 3.5),
                )
                self.set_destination("flee", flee_target)
                return

        if current_event == EVENT_PURGE and len(nearby_peeps) != 0:
            target, _ = closest_nearby_peep(nearby_peeps)
            if target is not None:
                self.set_destination("attack", target.position)
                return

        if self.mood_band() == "fury" and len(nearby_peeps) != 0:
            if random.randint(1, 100) <= 70:
                target, _ = closest_nearby_peep(nearby_peeps)
                if target is not None:
                    self.set_destination("attack", target.position)
                    return

        # adds spice to actions, everyone was too predictable
        spread_desire = self.wander_bias + random.randrange(25, 70)
        food_desire = self.food_bias + random.randrange(0, 28)
        church_desire = self.church_bias + random.randrange(0, 20)
        god_desire = -100

        # trying to avoid the church <-> kfc loop
        if self.last_destination in ("kfc", "church", "god"):
            spread_desire += 32

        if self.hunger < 58:
            food_desire += int((58 - self.hunger) * 1.4)

        if self.wealth < 10:
            food_desire -= 12

        # Stop peeps visiting kfc during shutdown
        if current_event == EVENT_KFC_CLOSED:
            food_desire = -100

        if self.last_destination == "kfc":
            food_desire -= 30

        if self.kfc_cooldown > 0:
            food_desire -= 16

        if self.religion < 42:
            church_desire += int((42 - self.religion) * 1.6)

        church_desire += int(self.church_urge * 18.0)

        if self.mood_band() in ("amazing", "excited"):
            church_desire += 6

        # Stop peeps from visiting church during shutdown
        if current_event == EVENT_CHURCH_CLOSED:
            church_desire = -100

        if self.last_destination == "church":
            church_desire -= 36

        if self.church_cooldown > 0:
            church_desire -= 24

        if current_event == EVENT_GOD_RISEN:
            god_desire = 20 + self.god_bias + random.randrange(5, 40)
            if self.religion < 70:
                god_desire += int((70 - self.religion) * 0.8)
            if distance_between(self.position, event_actor.position) < (
                EVENT_ACTOR_RADIUS * 2.0
            ):
                god_desire += 18
            if self.last_destination == "god":
                god_desire -= 20

        best_action = "wander"
        best_score = spread_desire

        if food_desire > best_score:
            best_action = "kfc"
            best_score = food_desire
        if church_desire > best_score:
            best_action = "church"
            best_score = church_desire
        if god_desire > best_score:
            best_action = "god"
            best_score = god_desire

        if best_action == "kfc":
            self.set_destination("kfc", random_point_near(KFC_POSITION, 1.6))
            return
        if best_action == "church":
            self.set_destination("church", random_point_near(CHURCH_POSITION, 1.8))
            return
        if best_action == "god" and event_actor is not None:
            self.set_destination("god", random_point_near(event_actor.position, 1.8))
            return

        self.set_destination("wander", random_wander_point())

    # Simulation Tick.
    def tick(self):

        self.apply_passive_changes()
        self.update_move_speed()

        # Handle queued movement actions
        if len(self.movement_actions) != 0:
            previous_position = list(self.position)
            self.position = self.movement_actions[0]
            self.movement_actions.pop(0)  # remove from queue
            
            # Now look towards next move point if one exists.
            # This needs to be cleaned and refractored before release
            if len(self.movement_actions) != 0:
                direciton = np.array(self.movement_actions[0]) - np.array(self.position)
                norm = np.linalg.norm(direciton)
                normalised = direciton / norm
                #print(f"dbg {normalised_vec2}")
                self.mesh.transform.rotate[1] = np.arctan2(normalised[0], normalised[2]) + math.tau/4
                #print(f"dbg {np.arctan2(normalised[0], normalised[2])}")

            self.transfer_movement()  # updates the mesh

             

        # Mood handling
        self.handle_arrival()
        self.calculate_mood()

        nearby_peeps = self.get_nearby_peeps(MOOD_RADIUS)
        self.apply_mood_effects(nearby_peeps)

        # Action handling
        if self.mood_band() == "fury" or current_event == EVENT_PURGE:
            self.try_attack(nearby_peeps)

        if len(self.movement_actions) == 0:
            self.choose_next_action(nearby_peeps)

        # recalc mood and color acordingly
        self.calculate_mood()
        self.update_visuals()

    # Update the mesh colour from the current mood band.
    def update_visuals(self):
        colors = {
            "amazing": (110, 255, 140),
            "excited": (220, 255, 90),
            "happy": (69, 171, 10),
            "content": (150, 170, 160),
            "sad": (90, 140, 210),
            "irritated": (220, 150, 60),
            "angry": (220, 80, 60),
            "fury": (120, 20, 20),
        }
        self.mesh.color = colors[self.mood_band()]

    # transfer the peep position to mesh -> transform.
    def transfer_movement(self):
        self.mesh.transform.translate[0] = self.position[0]
        self.mesh.transform.translate[1] = self.position[1]
        self.mesh.transform.translate[2] = self.position[2]
        self.mesh.transform.update_model()

    # Queue movement steps toward a point.
    def move_to(self, point):
        start = self.position
        if len(self.movement_actions) != 0:
            start = self.movement_actions[-1]
        self.movement_actions += lerp_vector3(start, point, self.move_speed)


# Creates a interpolated actions list between points.
def lerp_vector3(vec1, vec2, step_distance):
    start = np.array(vec1, dtype=float)
    finish = np.array(vec2, dtype=float)
    distance = np.linalg.norm(finish - start)
    if distance == 0:
        return []

    steps = max(1, int(np.ceil(distance / max(step_distance, 0.001))))
    increments = []

    for step in range(steps):
        amount = float(step + 1) / float(steps)
        increments.append(
            [
                vec1[0] + ((vec2[0] - vec1[0]) * amount),
                vec1[1] + ((vec2[1] - vec1[1]) * amount),
                vec1[2] + ((vec2[2] - vec1[2]) * amount),
            ]
        )
    return increments
