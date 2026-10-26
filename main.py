"""PawPal+ demo: build a sample owner with two pets and print today's schedule."""

from pawpal_system import Owner, Pet, Task, Scheduler


def create_sample_owner() -> Owner:
    """Create Jordan, their two pets, and a set of care tasks."""
    owner = Owner("Jordan", available_minutes=90, preferences=["walk", "meds"])

    mochi = Pet("Mochi", species="dog", age=3)
    luna = Pet("Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Mochi's tasks
    mochi.add_task(Task("Morning walk", 30, priority="high", category="walk",
                        preferred_time="morning", time="08:00", recurrence="daily"))
    mochi.add_task(Task("Breakfast", 10, priority="high", category="feeding",
                        preferred_time="morning", time="07:30", recurrence="daily"))
    mochi.add_task(Task("Bath and brush", 45, priority="low", category="grooming",
                        preferred_time="afternoon", time="15:00"))

    # Luna's tasks
    luna.add_task(Task("Thyroid medication", 5, priority="high", category="meds",
                       preferred_time="morning", time="09:00", recurrence="daily"))
    luna.add_task(Task("Dinner", 10, priority="medium", category="feeding",
                       preferred_time="evening", time="18:00", recurrence="daily"))

    return owner


def print_schedule(scheduler: Scheduler) -> None:
    """Print today's scheduled tasks and any skipped tasks in a readable table."""
    owner = scheduler.owner
    print("=" * 60)
    print(f"  Today's Schedule for {owner.name}  ({scheduler.plan_date})")
    print("=" * 60)

    print(f"{'Time':<7}{'Pet':<8}{'Task':<22}{'Duration':<10}{'Priority'}")
    print("-" * 60)
    for task in scheduler.scheduled_tasks:
        print(f"{task.time:<7}{task.pet_name:<8}{task.title:<22}"
              f"{str(task.duration_minutes) + ' min':<10}{task.priority}")

    used = scheduler.total_scheduled_minutes()
    print("-" * 60)
    print(f"Time used: {used} of {owner.available_minutes} minutes")

    if scheduler.skipped_tasks:
        print("\nSkipped tasks:")
        minutes_left = owner.available_minutes - used
        for task in scheduler.skipped_tasks:
            print(f"  - {task.title} for {task.pet_name} ({task.priority} priority): "
                  f"needs {task.duration_minutes} min, but only {minutes_left} min were left")

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("\nWarnings:")
        for warning in conflicts:
            print(f"  - {warning}")


def main() -> None:
    """Build the sample data, generate a daily plan, and print it."""
    owner = create_sample_owner()
    scheduler = Scheduler(owner)
    scheduler.build_daily_plan()
    print_schedule(scheduler)


if __name__ == "__main__":
    main()
