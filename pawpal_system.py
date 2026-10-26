"""PawPal+ core system: owners, pets, care tasks, and daily scheduling.

See diagrams/uml.mmd for the matching class diagram.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import Optional

PRIORITY_RANKS = {"low": 1, "medium": 2, "high": 3}
TIME_OF_DAY_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, "any": 3}
RECURRENCE_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low", "medium", or "high"
    category: str = "general"  # e.g. "walk", "feeding", "grooming", "meds"
    preferred_time: str = "any"  # e.g. "morning", "afternoon", "evening", "any"
    time: str = ""  # specific scheduled time as "HH:MM"; empty means unscheduled
    due_date: date = field(default_factory=date.today)
    pet_name: str = ""  # set by Pet.add_task()
    completed: bool = False
    recurrence: str = "none"  # e.g. "none", "daily", "weekly"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def priority_value(self) -> int:
        """Return a numeric rank for this task's priority (higher = more important)."""
        return PRIORITY_RANKS.get(self.priority.lower(), PRIORITY_RANKS["medium"])

    def next_occurrence(self) -> Optional[Task]:
        """Return a new, incomplete copy of this task for its next due date, or None if it does not recur."""
        interval = RECURRENCE_INTERVALS.get(self.recurrence.lower())
        if interval is None:
            return None
        return replace(self, due_date=self.due_date + interval, completed=False)

    def identity(self) -> tuple[str, str, date, str]:
        """Return a key identifying this task occurrence, used to detect duplicates."""
        return (self.pet_name, self.title.lower(), self.due_date, self.time)


@dataclass
class Pet:
    """A pet owned by an Owner, holding the care tasks it needs."""

    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet and set the task's pet_name, ignoring duplicates."""
        task.pet_name = self.name
        if any(existing.identity() == task.identity() for existing in self.tasks):
            return
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove every task with the given title (case-insensitive) from this pet."""
        remaining = [t for t in self.tasks if t.title.lower() != title.lower()]
        if len(remaining) == len(self.tasks):
            raise ValueError(f"{self.name} has no task titled '{title}'.")
        self.tasks = remaining

    def get_pending_tasks(self) -> list[Task]:
        """Return this pet's tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]


class Owner:
    """A pet owner with a daily time budget, preferred task categories, and one or more pets."""

    def __init__(
        self,
        name: str,
        available_minutes: int,
        preferences: Optional[list[str]] = None,
        pets: Optional[list[Pet]] = None,
    ) -> None:
        """Create an owner; preferences and pets default to empty lists."""
        self.name: str = name
        self.available_minutes: int = available_minutes
        # Preferred task categories (e.g. "walk", "meds") to favor when scheduling
        self.preferences: list[str] = preferences if preferences is not None else []
        self.pets: list[Pet] = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner, rejecting a duplicate pet name."""
        if any(p.name.lower() == pet.name.lower() for p in self.pets):
            raise ValueError(f"{self.name} already has a pet named '{pet.name}'.")
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name (case-insensitive) from this owner."""
        remaining = [p for p in self.pets if p.name.lower() != pet_name.lower()]
        if len(remaining) == len(self.pets):
            raise ValueError(f"{self.name} has no pet named '{pet_name}'.")
        self.pets = remaining

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds a daily care plan for an Owner's pets within their available time."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the given owner with an empty plan."""
        self.owner: Owner = owner
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []
        self.plan_date: date = date.today()
        # Reason for each scheduled/skipped task, keyed by id(task)
        self._reasons: dict[int, str] = {}

    def collect_tasks(self) -> list[Task]:
        """Gather unique pending tasks due on or before the plan date from all of the owner's pets."""
        seen: set[tuple[str, str, date, str]] = set()
        collected: list[Task] = []
        for task in self.owner.get_all_tasks():
            if task.completed or task.due_date > self.plan_date:
                continue
            if task.identity() in seen:
                continue
            seen.add(task.identity())
            collected.append(task)
        return collected

    def _is_preferred(self, task: Task) -> bool:
        """Return True if the task's category is one of the owner's preferences."""
        return task.category.lower() in {p.lower() for p in self.owner.preferences}

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by priority, preferred category, preferred time, and duration."""
        return sorted(
            tasks,
            key=lambda t: (
                -t.priority_value(),
                not self._is_preferred(t),
                TIME_OF_DAY_ORDER.get(t.preferred_time.lower(), TIME_OF_DAY_ORDER["any"]),
                t.time or "99:99",  # tasks with a set clock time come first within a slot
                t.duration_minutes,
            ),
        )

    def build_daily_plan(self) -> list[Task]:
        """Reset the plan, then fill the day with tasks that fit the owner's available time and preferred categories."""
        self.scheduled_tasks = []
        self.skipped_tasks = []
        self._reasons = {}

        remaining = self.owner.available_minutes
        for task in self.sort_tasks(self.collect_tasks()):
            if task.duration_minutes <= remaining:
                remaining -= task.duration_minutes
                self.scheduled_tasks.append(task)
                self._reasons[id(task)] = self._schedule_reason(task)
            else:
                self.skipped_tasks.append(task)
                self._reasons[id(task)] = (
                    f"needs {task.duration_minutes} min but only {remaining} min left"
                )

        # Present the final plan in time-of-day order
        self.scheduled_tasks.sort(
            key=lambda t: (
                TIME_OF_DAY_ORDER.get(t.preferred_time.lower(), TIME_OF_DAY_ORDER["any"]),
                t.time or "99:99",
            )
        )
        return self.scheduled_tasks

    def _schedule_reason(self, task: Task) -> str:
        """Return a short explanation of why a task was scheduled."""
        parts = [f"{task.priority.lower()} priority"]
        if self._is_preferred(task):
            parts.append(f"preferred category '{task.category}'")
        if task.preferred_time.lower() != "any":
            parts.append(f"best in the {task.preferred_time.lower()}")
        if task.due_date < self.plan_date:
            parts.append(f"overdue since {task.due_date.isoformat()}")
        return ", ".join(parts)

    def total_scheduled_minutes(self) -> int:
        """Return the total duration of all scheduled tasks."""
        return sum(t.duration_minutes for t in self.scheduled_tasks)

    def explain_plan(self) -> str:
        """Return a human-readable explanation of what was scheduled or skipped and why."""
        lines = [
            f"Daily plan for {self.owner.name} on {self.plan_date.isoformat()} "
            f"({self.total_scheduled_minutes()}/{self.owner.available_minutes} min used):"
        ]
        if self.scheduled_tasks:
            lines.append("Scheduled:")
            for task in self.scheduled_tasks:
                when = task.time or task.preferred_time
                lines.append(
                    f"  - [{when}] {task.title} for {task.pet_name} "
                    f"({task.duration_minutes} min) — {self._reasons.get(id(task), '')}"
                )
        else:
            lines.append("No tasks scheduled.")
        if self.skipped_tasks:
            lines.append("Skipped:")
            for task in self.skipped_tasks:
                lines.append(
                    f"  - {task.title} for {task.pet_name} "
                    f"({task.priority.lower()} priority) — {self._reasons.get(id(task), '')}"
                )
        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("Conflicts:")
            lines.extend(f"  - {warning}" for warning in conflicts)
        return "\n".join(lines)

    def detect_conflicts(self) -> list[str]:
        """Return a warning message for each pair of tasks scheduled at the same date and time."""
        tasks = self.scheduled_tasks or self.collect_tasks()
        timed = [t for t in tasks if t.time]
        warnings: list[str] = []
        for i, first in enumerate(timed):
            for second in timed[i + 1 :]:
                if first.due_date == second.due_date and first.time == second.time:
                    warnings.append(
                        f"'{first.title}' ({first.pet_name}) and '{second.title}' "
                        f"({second.pet_name}) are both at {first.time} on {first.due_date.isoformat()}"
                    )
        return warnings

    def complete_task(self, pet: Pet, task: Task) -> Optional[Task]:
        """Mark a pet's task complete and add its next occurrence to the pet, if it recurs."""
        if task not in pet.tasks:
            raise ValueError(f"'{task.title}' is not one of {pet.name}'s tasks.")
        task.mark_complete()
        if task in self.scheduled_tasks:
            self.scheduled_tasks.remove(task)
        next_task = task.next_occurrence()
        if next_task is not None:
            pet.add_task(next_task)  # add_task ignores an already-existing occurrence
        return next_task
