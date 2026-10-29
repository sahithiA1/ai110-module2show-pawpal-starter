"""Basic tests for the PawPal+ Task, Pet, and Scheduler classes."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def make_scheduler_with_pet() -> tuple[Scheduler, Pet]:
    """Return a scheduler whose owner has one pet, Mochi, with no tasks."""
    owner = Owner("Jordan", available_minutes=90)
    pet = Pet("Mochi", species="dog", age=3)
    owner.add_pet(pet)
    return Scheduler(owner), pet


def test_task_completion():
    """mark_complete() should change a task's completed status to True."""
    task = Task("Morning walk", 30)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_task_addition():
    """add_task() should add one task to a pet's task list."""
    pet = Pet("Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", 10))

    assert len(pet.tasks) == 1


def test_completing_daily_task_creates_task_due_tomorrow():
    """complete_task() on a daily task should add a new incomplete copy due the next day."""
    scheduler, pet = make_scheduler_with_pet()
    task = Task("Breakfast", 10, priority="high", time="07:30", recurrence="daily")
    pet.add_task(task)

    next_task = scheduler.complete_task(pet, task)

    assert task.completed is True
    assert next_task in pet.tasks
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_completing_weekly_task_creates_task_due_in_seven_days():
    """complete_task() on a weekly task should add a new copy due seven days later."""
    scheduler, pet = make_scheduler_with_pet()
    task = Task("Bath", 45, recurrence="weekly")
    pet.add_task(task)

    next_task = scheduler.complete_task(pet, task)

    assert next_task in pet.tasks
    assert next_task.due_date == date.today() + timedelta(days=7)


def test_completing_non_recurring_task_creates_nothing():
    """complete_task() on a one-off task should not add another occurrence."""
    scheduler, pet = make_scheduler_with_pet()
    task = Task("Vet visit", 60)  # recurrence defaults to "none"
    pet.add_task(task)

    next_task = scheduler.complete_task(pet, task)

    assert next_task is None
    assert pet.tasks == [task]


def test_next_occurrence_keeps_task_details():
    """The next occurrence should keep the title, pet, priority, duration, and time."""
    scheduler, pet = make_scheduler_with_pet()
    task = Task("Thyroid meds", 5, priority="high", time="09:00", recurrence="daily")
    pet.add_task(task)

    next_task = scheduler.complete_task(pet, task)

    assert next_task is not task
    assert next_task.title == "Thyroid meds"
    assert next_task.pet_name == "Mochi"
    assert next_task.priority == "high"
    assert next_task.duration_minutes == 5
    assert next_task.time == "09:00"
    assert next_task.recurrence == "daily"


def test_completing_task_twice_does_not_duplicate_next_occurrence():
    """Completing the same recurring task again should not add a second copy of its next occurrence."""
    scheduler, pet = make_scheduler_with_pet()
    task = Task("Morning walk", 30, time="08:00", recurrence="daily")
    pet.add_task(task)

    scheduler.complete_task(pet, task)
    scheduler.complete_task(pet, task)

    assert len(pet.tasks) == 2  # the original plus one next occurrence


def test_overdue_recurring_task_is_rescheduled_from_today():
    """An overdue daily task should get its next occurrence counted from today, not its old due date."""
    scheduler, pet = make_scheduler_with_pet()
    task = Task("Dinner", 10, recurrence="daily", due_date=date.today() - timedelta(days=8))
    pet.add_task(task)

    next_task = scheduler.complete_task(pet, task)

    assert next_task.due_date == date.today() + timedelta(days=1)


def make_scheduler_with_two_pets() -> tuple[Scheduler, Pet, Pet]:
    """Return a scheduler whose owner has two pets, Mochi and Luna, with no tasks."""
    scheduler, mochi = make_scheduler_with_pet()
    luna = Pet("Luna", species="cat", age=5)
    scheduler.owner.add_pet(luna)
    return scheduler, mochi, luna


def test_tasks_at_same_time_conflict():
    """Two tasks starting at the same time on the same date should produce one warning."""
    scheduler, mochi, luna = make_scheduler_with_two_pets()
    mochi.add_task(Task("Morning walk", 30, time="08:00"))
    luna.add_task(Task("Breakfast", 10, time="08:00"))

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "Morning walk" in warnings[0] and "Breakfast" in warnings[0]
    assert "08:00" in warnings[0]


def test_overlapping_durations_conflict_for_same_pet():
    """A task starting before another of the same pet's tasks has finished should be flagged."""
    scheduler, mochi = make_scheduler_with_pet()
    mochi.add_task(Task("Morning walk", 30, time="08:00"))  # 08:00-08:30
    mochi.add_task(Task("Brush teeth", 5, time="08:15"))

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "overlaps" in warnings[0]


def test_overlapping_durations_conflict_for_different_pets():
    """Overlaps should be flagged across pets, regardless of the order tasks were added."""
    scheduler, mochi, luna = make_scheduler_with_two_pets()
    luna.add_task(Task("Thyroid meds", 5, time="09:10"))
    mochi.add_task(Task("Park visit", 60, time="08:30"))  # 08:30-09:30

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert warnings[0].startswith("'Park visit'")  # the earlier task is named first


def test_same_time_on_different_dates_does_not_conflict():
    """Tasks at the same clock time on different dates should not be flagged."""
    scheduler, mochi, luna = make_scheduler_with_two_pets()
    today = date.today()
    mochi.add_task(Task("Morning walk", 30, time="08:00", due_date=today))
    luna.add_task(Task("Breakfast", 10, time="08:00", due_date=today - timedelta(days=1)))

    assert scheduler.detect_conflicts() == []


def test_back_to_back_and_untimed_tasks_do_not_conflict():
    """A task starting exactly when another ends, or with no time, should not be flagged."""
    scheduler, mochi = make_scheduler_with_pet()
    mochi.add_task(Task("Morning walk", 30, time="08:00"))  # ends at 08:30
    mochi.add_task(Task("Breakfast", 10, time="08:30"))
    mochi.add_task(Task("Play", 20))  # no time
    mochi.add_task(Task("Dinner", 10, time="18:00"))

    assert scheduler.detect_conflicts() == []


@pytest.mark.parametrize("time", ["08:00", "18:30", "8:05", "00:00", "23:59"])
def test_valid_times_are_accepted(time):
    """A valid 24-hour time should create the task without errors."""
    task = Task("Walk", 30, time=time)

    assert task.time == time


def test_empty_time_is_allowed():
    """A task without a scheduled time should keep an empty time string."""
    task = Task("Play", 20)

    assert task.time == ""


@pytest.mark.parametrize("time", ["8am", "25:99", "12:60", "24:00", "hello"])
def test_invalid_times_raise_value_error(time):
    """An invalid time should raise a ValueError that explains the expected format."""
    with pytest.raises(ValueError, match="24-hour HH:MM format"):
        Task("Walk", 30, time=time)


def test_sort_by_time_orders_tasks_chronologically_with_untimed_last():
    """sort_by_time() should order tasks by clock time, put untimed tasks last, and not change the input list."""
    scheduler, _ = make_scheduler_with_pet()
    tasks = [
        Task("Dinner", 10, time="20:00"),
        Task("Play", 20),  # no time
        Task("Meds", 5, time="8:05"),  # single-digit hour must still sort before "20:00"
        Task("Breakfast", 10, time="07:30"),
        Task("Lunch", 10, time="12:00"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [t.title for t in sorted_tasks] == ["Breakfast", "Meds", "Lunch", "Dinner", "Play"]
    assert tasks[0].title == "Dinner"  # original list is unchanged


def make_scheduler_with_mixed_tasks() -> Scheduler:
    """Return a scheduler with two pets, each with one completed and one or two pending tasks."""
    scheduler, mochi, luna = make_scheduler_with_two_pets()
    mochi.add_task(Task("Morning walk", 30, time="08:00"))
    mochi.add_task(Task("Breakfast", 10, time="07:30"))
    mochi.add_task(Task("Bath", 45))
    luna.add_task(Task("Thyroid meds", 5, time="09:00"))
    luna.add_task(Task("Dinner", 10, time="18:00"))
    mochi.tasks[1].mark_complete()  # Mochi's Breakfast
    luna.tasks[0].mark_complete()  # Luna's Thyroid meds
    return scheduler


def test_filter_tasks_by_pet_name_is_case_insensitive():
    """Filtering by pet name should match regardless of capitalization."""
    scheduler = make_scheduler_with_mixed_tasks()

    for name in ("luna", "LUNA", "Luna"):
        assert [t.title for t in scheduler.filter_tasks(pet_name=name)] == ["Thyroid meds", "Dinner"]


def test_filter_tasks_by_completion_status():
    """Filtering by completed=True or completed=False should return only matching tasks."""
    scheduler = make_scheduler_with_mixed_tasks()

    completed = scheduler.filter_tasks(completed=True)
    pending = scheduler.filter_tasks(completed=False)

    assert [t.title for t in completed] == ["Breakfast", "Thyroid meds"]
    assert [t.title for t in pending] == ["Morning walk", "Bath", "Dinner"]


def test_filter_tasks_with_pet_name_and_status_combined():
    """Using both filters should return only tasks that match the pet and the status."""
    scheduler = make_scheduler_with_mixed_tasks()

    mochi_pending = scheduler.filter_tasks(pet_name="Mochi", completed=False)

    assert [t.title for t in mochi_pending] == ["Morning walk", "Bath"]


def test_filter_tasks_with_unknown_pet_returns_empty_list():
    """Filtering by a pet the owner does not have should return an empty list, not raise an error."""
    scheduler = make_scheduler_with_mixed_tasks()

    assert scheduler.filter_tasks(pet_name="Rex") == []


def test_filter_tasks_without_filters_returns_all_tasks():
    """Calling filter_tasks() with no arguments should return every task for every pet."""
    scheduler = make_scheduler_with_mixed_tasks()

    assert len(scheduler.filter_tasks()) == 5


def test_daily_plan_stays_within_available_minutes_and_prefers_high_priority():
    """build_daily_plan() should never use more than the owner's minutes, and should keep high-priority tasks over low ones."""
    scheduler, mochi = make_scheduler_with_pet()
    scheduler.owner.available_minutes = 60
    mochi.add_task(Task("Bath", 40, priority="low"))  # added first so ignoring priority would schedule it
    mochi.add_task(Task("Morning walk", 30, priority="high"))
    mochi.add_task(Task("Meds", 10, priority="high"))
    mochi.add_task(Task("Dinner", 15, priority="medium"))

    plan = scheduler.build_daily_plan()

    assert scheduler.total_scheduled_minutes() <= 60
    assert {t.title for t in plan} == {"Morning walk", "Meds", "Dinner"}
    assert [t.title for t in scheduler.skipped_tasks] == ["Bath"]


def test_daily_plan_skips_task_that_does_not_fit_but_keeps_filling_time():
    """A task too long for the remaining time should be skipped while smaller tasks after it are still scheduled."""
    scheduler, mochi = make_scheduler_with_pet()
    scheduler.owner.available_minutes = 40
    mochi.add_task(Task("Park visit", 30, priority="high"))
    mochi.add_task(Task("Hike", 35, priority="high"))  # only 10 min left after the park visit
    mochi.add_task(Task("Brush teeth", 5, priority="low"))

    plan = scheduler.build_daily_plan()

    assert {t.title for t in plan} == {"Park visit", "Brush teeth"}
    assert [t.title for t in scheduler.skipped_tasks] == ["Hike"]
    assert scheduler.total_scheduled_minutes() == 35


def test_daily_plan_schedules_tasks_that_exactly_fill_available_time():
    """Tasks whose durations add up to exactly the available minutes should all be scheduled."""
    scheduler, mochi = make_scheduler_with_pet()
    scheduler.owner.available_minutes = 30
    mochi.add_task(Task("Morning walk", 20))
    mochi.add_task(Task("Breakfast", 10))

    plan = scheduler.build_daily_plan()

    assert len(plan) == 2
    assert scheduler.skipped_tasks == []
    assert scheduler.total_scheduled_minutes() == 30


def test_daily_plan_is_empty_when_owner_has_zero_minutes():
    """An owner with no available time should get an empty plan, with every task skipped."""
    scheduler, mochi = make_scheduler_with_pet()
    scheduler.owner.available_minutes = 0
    mochi.add_task(Task("Breakfast", 10, priority="high"))

    assert scheduler.build_daily_plan() == []
    assert [t.title for t in scheduler.skipped_tasks] == ["Breakfast"]


def test_daily_plan_is_empty_for_owner_without_pets_or_tasks():
    """An owner with no pets, or a pet with no tasks, should get an empty plan without errors."""
    no_pets = Scheduler(Owner("Jordan", available_minutes=90))
    no_tasks, _ = make_scheduler_with_pet()

    for scheduler in (no_pets, no_tasks):
        assert scheduler.build_daily_plan() == []
        assert scheduler.skipped_tasks == []
        assert scheduler.detect_conflicts() == []
        assert scheduler.sort_by_time([]) == []
        assert "No tasks scheduled." in scheduler.explain_plan()


def test_daily_plan_includes_overdue_but_not_completed_or_future_tasks():
    """Today's plan should include overdue tasks and leave out completed tasks and tasks due later."""
    scheduler, mochi = make_scheduler_with_pet()
    today = date.today()
    done = Task("Already fed", 10)
    done.mark_complete()
    mochi.add_task(done)
    mochi.add_task(Task("Vet visit", 30, due_date=today + timedelta(days=1)))
    mochi.add_task(Task("Nail trim", 15, due_date=today - timedelta(days=2)))

    plan = scheduler.build_daily_plan()

    assert [t.title for t in plan] == ["Nail trim"]


def test_daily_plan_is_chronological_even_when_chosen_by_priority():
    """build_daily_plan() picks tasks by priority but should list the chosen tasks in time order."""
    scheduler, mochi = make_scheduler_with_pet()
    mochi.add_task(Task("Dinner", 10, priority="high", time="18:00"))
    mochi.add_task(Task("Play", 15, priority="low"))  # no time
    mochi.add_task(Task("Breakfast", 10, priority="low", time="07:00"))
    mochi.add_task(Task("Morning walk", 30, priority="medium", time="08:30"))

    plan = scheduler.build_daily_plan()

    assert [t.title for t in plan] == ["Breakfast", "Morning walk", "Dinner", "Play"]
