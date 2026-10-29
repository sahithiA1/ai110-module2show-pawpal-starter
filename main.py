"""PawPal+ demo: build a sample owner with two pets, print today's schedule, and show the smarter scheduling features."""

from pawpal_system import Owner, Pet, Task, Scheduler


def create_sample_owner() -> Owner:
    """Create Jordan, their two pets, and a set of care tasks added out of time order."""
    owner = Owner("Jordan", available_minutes=90, preferences=["walk", "meds"])

    mochi = Pet("Mochi", species="dog", age=3)
    luna = Pet("Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Mochi's tasks (deliberately not in time order)
    mochi.add_task(Task("Bath and brush", 45, priority="low", category="grooming",
                        preferred_time="afternoon", time="15:00"))
    mochi.add_task(Task("Morning walk", 30, priority="high", category="walk",
                        preferred_time="morning", time="08:00", recurrence="daily"))
    mochi.add_task(Task("Nail trim", 15, priority="medium", category="grooming",
                        preferred_time="afternoon", time="16:00", recurrence="weekly"))
    mochi.add_task(Task("Breakfast", 10, priority="high", category="feeding",
                        preferred_time="morning", time="07:30", recurrence="daily"))

    # Luna's tasks (deliberately not in time order)
    luna.add_task(Task("Dinner", 10, priority="medium", category="feeding",
                       preferred_time="evening", time="18:00", recurrence="daily"))
    luna.add_task(Task("Thyroid medication", 5, priority="high", category="meds",
                       preferred_time="morning", time="09:00", recurrence="daily"))
    # Starts during Mochi's 08:00-08:30 walk -> overlapping-duration conflict
    luna.add_task(Task("Litter box", 10, priority="medium", category="cleaning",
                       preferred_time="morning", time="08:15", recurrence="daily"))
    # Same time as Mochi's breakfast -> exact-time conflict
    luna.add_task(Task("Breakfast", 10, priority="high", category="feeding",
                       preferred_time="morning", time="07:30", recurrence="daily"))

    return owner


def print_heading(title: str) -> None:
    """Print a section heading."""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_tasks(tasks: list[Task]) -> None:
    """Print tasks one per line with time, pet, title, due date, and status."""
    if not tasks:
        print("  (no tasks)")
    for task in tasks:
        status = "done" if task.completed else "pending"
        print(f"  {task.time or '--:--':<7}{task.pet_name:<8}{task.title:<22}"
              f"due {task.due_date}  {status}")


def find_task(pet: Pet, title: str) -> Task:
    """Return the pet's first incomplete task with the given title."""
    return next(t for t in pet.get_pending_tasks() if t.title == title)


def print_schedule(scheduler: Scheduler) -> None:
    """Print today's scheduled tasks and any skipped tasks in a readable table."""
    owner = scheduler.owner
    print_heading(f"1. Today's Schedule for {owner.name}  ({scheduler.plan_date})")

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


def demo_sorting(scheduler: Scheduler) -> None:
    """Show every task in the order it was added, then sorted by time."""
    print_heading("2. Sorting by time")
    all_tasks = scheduler.owner.get_all_tasks()
    print("In the order they were added:")
    print_tasks(all_tasks)
    print("\nAfter sort_by_time():")
    print_tasks(scheduler.sort_by_time(all_tasks))


def demo_recurrence(scheduler: Scheduler, mochi: Pet) -> None:
    """Complete a daily and a weekly task and show the next occurrence each one creates."""
    print_heading("3. Recurring tasks")
    for title in ("Breakfast", "Nail trim"):
        task = find_task(mochi, title)
        next_task = scheduler.complete_task(mochi, task)
        print(f"Completed {mochi.name}'s '{task.title}' ({task.recurrence}, due {task.due_date})")
        print(f"  -> next '{next_task.title}' due {next_task.due_date} "
              f"at {next_task.time}, completed={next_task.completed}")


def demo_filtering(scheduler: Scheduler) -> None:
    """Filter tasks by pet name, completion status, and both together."""
    print_heading("4. Filtering tasks")
    print("filter_tasks(pet_name='luna'):")
    print_tasks(scheduler.sort_by_time(scheduler.filter_tasks(pet_name="luna")))
    print("\nfilter_tasks(completed=True):")
    print_tasks(scheduler.filter_tasks(completed=True))
    print("\nfilter_tasks(pet_name='Mochi', completed=False):")
    print_tasks(scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi", completed=False)))


def main() -> None:
    """Build the sample data, print today's plan, then demonstrate sorting, recurrence, and filtering."""
    owner = create_sample_owner()
    mochi = owner.pets[0]
    scheduler = Scheduler(owner)

    # Show the original plan before anything is marked complete
    scheduler.build_daily_plan()
    print_schedule(scheduler)

    demo_sorting(scheduler)
    demo_recurrence(scheduler, mochi)
    demo_filtering(scheduler)


if __name__ == "__main__":
    main()
