"""PawPal+ core system: class skeletons for owners, pets, tasks, and scheduling.

Design phase only — method bodies are intentionally left unimplemented.
See diagrams/uml.mmd for the matching class diagram.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low", "medium", or "high"
    category: str = "general"  # e.g. "walk", "feeding", "grooming", "meds"
    preferred_time: str = "any"  # e.g. "morning", "afternoon", "evening", "any"
    completed: bool = False
    recurrence: str = "none"  # e.g. "none", "daily", "weekly"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        raise NotImplementedError

    def priority_value(self) -> int:
        """Return a numeric rank for this task's priority (higher = more important)."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet owned by an Owner, holding the care tasks it needs."""

    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        raise NotImplementedError

    def remove_task(self, title: str) -> None:
        """Remove the task with the given title from this pet."""
        raise NotImplementedError

    def get_pending_tasks(self) -> list[Task]:
        """Return this pet's tasks that are not yet completed."""
        raise NotImplementedError


class Owner:
    """A pet owner with a daily time budget, care preferences, and one or more pets."""

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
        self.preferences: list[str] = preferences if preferences is not None else []
        self.pets: list[Pet] = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name from this owner."""
        raise NotImplementedError

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        raise NotImplementedError


class Scheduler:
    """Builds a daily care plan for an Owner's pets within their available time."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the given owner with an empty plan."""
        self.owner: Owner = owner
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []

    def collect_tasks(self) -> list[Task]:
        """Gather all pending tasks from the owner's pets."""
        raise NotImplementedError

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by priority, preferred time, and duration."""
        raise NotImplementedError

    def build_daily_plan(self) -> list[Task]:
        """Fill the day with tasks that fit the owner's available time and preferences."""
        raise NotImplementedError

    def total_scheduled_minutes(self) -> int:
        """Return the total duration of all scheduled tasks."""
        raise NotImplementedError

    def explain_plan(self) -> str:
        """Return a human-readable explanation of what was scheduled or skipped and why."""
        raise NotImplementedError

    def detect_conflicts(self) -> list[Task]:
        """Return tasks that conflict with each other (e.g. overlapping time slots)."""
        raise NotImplementedError

    def handle_recurring_tasks(self) -> list[Task]:
        """Return the next occurrences of completed recurring tasks."""
        raise NotImplementedError
