# Write the final report files.

from datetime import datetime
from pathlib import Path

RESULTS_PATH = Path("./results.md")

MOOD_NAMES = (
    "amazing",
    "excited",
    "happy",
    "content",
    "sad",
    "irritated",
    "angry",
    "fury",
)


# Helper function.
# Had issues with inf.
def average(total, count):
    if count == 0:
        return 0.0
    return total / count


# Get (avg, min, max) for a peep atribute.
def get_stats(peeps, attribute_name):
    if len(peeps) == 0:
        return 0.0, 0.0, 0.0

    # Init the min max stats.
    first_value = getattr(peeps[0], attribute_name)
    total = 0.0
    minimum = first_value
    maximum = first_value

    # Iter and check.
    for peep in peeps:
        value = getattr(peep, attribute_name)
        total += value
        if value < minimum:
            minimum = value
        if value > maximum:
            maximum = value

    return average(total, len(peeps)), minimum, maximum


# Sum of peeps in each mood.
def count_moods(peeps):
    # Init.
    counts = {}
    for mood_name in MOOD_NAMES:
        counts[mood_name] = 0

    # Iter.
    for peep in peeps:
        counts[peep.mood_band()] += 1

    return counts


# Tracker class to hold session stats.
class SessionTracker:
    # Store data collected during one run.
    def __init__(self, config, tickrate):
        self.config = dict(config)
        self.tickrate = tickrate
        self.start_time = datetime.now()

        self.tick_count = 0

        self.final_avg_hapiness = 0.0
        self.avg_hapiness_total = 0.0
        self.lowest_avg_hapiness = None
        self.highest_avg_hapiness = None

        self.event_counts = {}
        self.event_active_ticks = {}
        self.last_event = None

    # Record one simulation tick.
    def record_tick(self, peeps, event_name, average_hapiness):
        self.tick_count += 1

        self.final_avg_hapiness = average_hapiness
        self.avg_hapiness_total += average_hapiness

        if (
            self.lowest_avg_hapiness is None
            or average_hapiness < self.lowest_avg_hapiness
        ):
            self.lowest_avg_hapiness = average_hapiness
        if (
            self.highest_avg_hapiness is None
            or average_hapiness > self.highest_avg_hapiness
        ):
            self.highest_avg_hapiness = average_hapiness

        if event_name not in self.event_active_ticks:
            self.event_active_ticks[event_name] = 0
        self.event_active_ticks[event_name] += 1

        if event_name != self.last_event:
            if event_name != "none":
                if event_name not in self.event_counts:
                    self.event_counts[event_name] = 0
                self.event_counts[event_name] += 1
            self.last_event = event_name

    # Write the final markdown results file.
    def write_results(self, peeps):
        end_time = datetime.now()
        average_hapiness = average(self.avg_hapiness_total, self.tick_count)
        runtime_seconds = (end_time - self.start_time).total_seconds()

        lowest_avg_hapiness = self.lowest_avg_hapiness
        highest_avg_hapiness = self.highest_avg_hapiness

        hunger_avg, hunger_min, hunger_max = get_stats(peeps, "hunger")
        social_avg, social_min, social_max = get_stats(peeps, "social")
        religion_avg, religion_min, religion_max = get_stats(peeps, "religion")
        wealth_avg, wealth_min, wealth_max = get_stats(peeps, "wealth")
        moods = count_moods(peeps)

        lines = []
        lines.append("# Emotion Simulation Results")
        lines.append("")
        lines.append(
            f"- Started: `{self.start_time.isoformat(sep=' ', timespec='seconds')}`"
        )
        lines.append(f"- Ended: `{end_time.isoformat(sep=' ', timespec='seconds')}`")
        lines.append(f"- Runtime: `{runtime_seconds:.2f}s`")
        lines.append("")

        lines.append("## Happiness")
        lines.append("")
        lines.append(f"- Final Average Hapiness: `{self.final_avg_hapiness:.2f}`")
        lines.append(f"- Session Average Hapiness: `{average_hapiness:.2f}`")
        lines.append(f"- Lowest Average Hapiness: `{lowest_avg_hapiness:.2f}`")
        lines.append(f"- Highest Average Hapiness: `{highest_avg_hapiness:.2f}`")
        lines.append("")

        lines.append("## Final Attributes")
        lines.append("")
        lines.append("| Attribute | Average | Min | Max |")
        lines.append("| --- | ---: | ---: | ---: |")
        lines.append(
            f"| Hunger | {hunger_avg:.2f} | {hunger_min:.2f} | {hunger_max:.2f} |"
        )
        lines.append(
            f"| Social | {social_avg:.2f} | {social_min:.2f} | {social_max:.2f} |"
        )
        lines.append(
            f"| Religion | {religion_avg:.2f} | {religion_min:.2f} | {religion_max:.2f} |"
        )
        lines.append(
            f"| Wealth | {wealth_avg:.2f} | {wealth_min:.2f} | {wealth_max:.2f} |"
        )
        lines.append("")

        lines.append("## Final Mood Spread")
        lines.append("")
        lines.append("| Mood | Peeps |")
        lines.append("| --- | ---: |")
        for mood_name in MOOD_NAMES:
            lines.append(f"| {mood_name} | {moods[mood_name]} |")
        lines.append("")

        lines.append("## Events")
        lines.append("")
        lines.append("| Name | Occurences | Total Duration (S) |")
        lines.append("| --- | ---: | ---: |")
        if len(self.event_counts) == 0:
            lines.append("- No events were triggered during this run.")
        else:
            for event_name in sorted(self.event_counts):
                active_ticks = self.event_active_ticks.get(event_name, 0)
                active_seconds = (active_ticks * self.tickrate) / 1000.0
                lines.append(
                    f"| {event_name} | {self.event_counts[event_name]} | {active_seconds:.2f} |"
                )
        lines.append("")

        RESULTS_PATH.write_text("\n".join(lines), encoding="utf-8")
