import random
import numpy as np


class Peep:
    def __init__(self, mesh):
        # Emotion logic
        self.recovery_rate = random.randrange(
            7, 10
        )  # How many seconds it stays in a mood
        self.hunger = random.randrange(
            50, 100
        )  # Drains over time, can replenish with food
        self.social = random.randrange(
            50, 100
        )  # Gets affected by nearby peeps hapiness
        self.religion = random.randrange(
            50, 100
        )  # Increases by seeing miricles and visitng the church. affects chance of going to church
        self.wealth = random.randrange(
            50, 100
        )  # Increased by stealing, being poor makes you more likely to steal
        self.prefrences = [
            random.randrange(0, 32),
            random.randrange(0, 32),
            random.randrange(0, 32),
        ]
        self.prefrences.append(
            1 - self.prefrences[0] - self.prefrences[1] - self.prefrences[2]
        )
        # Prefence How much they prefer each attribute. makes them gain it faster and increases its hapiness gain

        # Engine Atributes
        self.mesh = mesh
        self.position = [
            0,
            0,
            0,
        ]  # Should make it randomly around later, but orgin for now
        self.movement_actions = []  # Used for lerping between points
        self.move_speed = 0.1  # Default move speed, gets overwritten by config

    def calculate_mood(self):
        self.mood = (
            (self.hunger * self.prefrences[0])
            + (self.social * self.prefrences[1])
            + (self.religion * self.prefrences[2])
            + (self.wealth * self.prefrences[3])
        )

    # Used for each tick of a peeps logic, peeps should tick every 0.1 seconds.
    def tick(self):
        # Handle movement actions IF THERE IS ONE
        if len(self.movement_actions) != 0:
            self.position = self.movement_actions[0]
            self.movement_actions.pop(0)  # Action done, remove from list
            self.transfer_movement()

    # Because mesh is a seperate class we need to pass it our position info and recalc our model mat4
    def transfer_movement(self):
        self.mesh.transform.translate[0] = self.position[0]
        self.mesh.transform.translate[1] = self.position[1]
        self.mesh.transform.translate[2] = self.position[2]
        self.mesh.transform.update_model()

    # Given a Vector 3, add lerped moveto actions
    def move_to(self, point):
        start = (
            self.position
            if len(self.movement_actions) == 0
            else self.movement_actions[-1]
        )
        self.movement_actions += lerp_vector3(start, point, self.move_speed)


def linear_lerp(from_float: float, to_float: float, step, steps: int):
    increments = (to_float - from_float) / float(steps)
    return from_float + increments * (1 + step)


def lerp_vector3(vec1, vec2, step_distance):
    mov_vec = np.array(np.array(vec2) - np.array(vec1))
    steps = round(np.linalg.norm(mov_vec) / step_distance)

    increments = []
    for step in range(steps):
        increments.append(
            [
                linear_lerp(vec1[0], vec2[0], step, steps),
                linear_lerp(vec1[1], vec2[1], step, steps),
                linear_lerp(vec1[2], vec2[2], step, steps),
            ]
        )
    return increments


if __name__ == "__main__":
    print(linear_lerp(7.1, 13.2, 5, 10))
    print("lerp from -5,0,0 to 5,10,10")
    print(lerp_vector3((-5, 0, 0), (5, 10, 10), 2))
