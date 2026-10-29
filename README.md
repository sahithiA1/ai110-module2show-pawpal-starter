# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Implementation Summary

The core logic lives in `pawpal_system.py` and is built from four classes:

- **Task** is a single care activity, such as a walk, feeding, medication, or grooming. It stores the duration, priority, category, preferred time, an optional scheduled time (`"HH:MM"`), due date, and whether the task repeats. It checks that its scheduled time is valid when it is created, can mark itself complete, and can create its next occurrence (daily or weekly).
- **Pet** holds its own list of tasks. It can add tasks (ignoring duplicates), remove them, and return the ones still pending.
- **Owner** has a name, a daily time budget (`available_minutes`), preferred task categories, and one or more pets.
- **Scheduler** builds the daily plan for one owner. It chooses tasks by priority, preferred category, and time of day, adding them until the owner's available minutes run out, and then displays the chosen tasks in chronological order. It records why each task was scheduled or skipped, warns about overlapping tasks, filters tasks, and adds the next occurrence when a recurring task is completed. See [Smarter Scheduling](#-smarter-scheduling) for details.

The Scheduler does not read tasks from a single pet. It gets them from `Owner.get_all_tasks()`, which combines the tasks of every pet the owner has, so one plan covers all of the owner's pets.

## 🖥️ Sample Output

Run the CLI demo to generate today's schedule for Jordan's pets, Mochi and Luna:

```bash
python3 main.py
```

The demo prints four numbered sections:

1. **Today's Schedule:** the daily plan in time order, the skipped task, and conflict warnings.
2. **Sorting by time:** every task in the order it was added, then after `sort_by_time()`.
3. **Recurring tasks:** a daily and a weekly task are completed, and their next occurrences are shown.
4. **Filtering tasks:** tasks filtered by pet name, by completion status, and by both.

The first and third sections look like this (the dates depend on the day you run it):

```text
============================================================
  1. Today's Schedule for Jordan  (2026-10-29)
============================================================
Time   Pet     Task                  Duration  Priority
------------------------------------------------------------
07:30  Mochi   Breakfast             10 min    high
07:30  Luna    Breakfast             10 min    high
08:00  Mochi   Morning walk          30 min    high
08:15  Luna    Litter box            10 min    medium
09:00  Luna    Thyroid medication    5 min     high
16:00  Mochi   Nail trim             15 min    medium
18:00  Luna    Dinner                10 min    medium
------------------------------------------------------------
Time used: 90 of 90 minutes

Skipped tasks:
  - Bath and brush for Mochi (low priority): needs 45 min, but only 0 min were left

Warnings:
  - 'Breakfast' (Mochi) and 'Breakfast' (Luna) are both at 07:30 on 2026-10-29
  - 'Morning walk' (Mochi, 08:00, 30 min) overlaps 'Litter box' (Luna, 08:15) on 2026-10-29

...

============================================================
  3. Recurring tasks
============================================================
Completed Mochi's 'Breakfast' (daily, due 2026-10-29)
  -> next 'Breakfast' due 2026-10-30 at 07:30, completed=False
Completed Mochi's 'Nail trim' (weekly, due 2026-10-29)
  -> next 'Nail trim' due 2026-11-05 at 16:00, completed=False
```

## Testing PawPal+

### Running the tests

On macOS, run the full test suite from the project folder with:

```bash
python3 -m pytest
```

The assignment instructions use `python -m pytest`, which runs the same tests. On many Macs, `python` is not available or points to an older version, so `python3` is the safer choice.

Other useful options:

```bash
# Shorter output (one dot per test):
python3 -m pytest -q

# Run with coverage (requires: pip install pytest-cov):
python3 -m pytest --cov=pawpal_system
```

### Test results

Output from the latest run (the `rootdir` path is shortened to the project folder name for display):

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.7, pytest-7.4.4, pluggy-1.0.0
rootdir: ai110-module2show-pawpal-starter
plugins: anyio-4.2.0
collected 37 items

tests/test_pawpal.py .....................................               [100%]

============================== 37 passed in 0.08s ==============================
```

### What the tests cover

The 37 tests in `tests/test_pawpal.py` cover:

- **Task creation and completion:** marking a task complete and adding a task to a pet.
- **Sorting:** out-of-order times (including `"8:05"` vs `"20:00"`), untimed tasks going last, and leaving the original list unchanged.
- **Filtering:** case-insensitive pet names, completed and pending tasks, both filters combined, an unknown pet name, and no filters.
- **Recurring tasks:** daily and weekly next occurrences, non-recurring tasks, keeping task details, avoiding duplicates, and overdue tasks.
- **Conflict detection:** exact-time conflicts, overlapping durations for the same pet and for different pets, and cases that should not be flagged (different dates, back-to-back tasks, and tasks without a time).
- **Time validation:** valid times, an empty time, and invalid times.
- **Daily plan (`build_daily_plan()`):**
  - Scheduling priorities: high-priority tasks are kept over low-priority ones.
  - Available-minute limits: the plan never goes over the owner's time, a task that does not fit is skipped while smaller tasks still get scheduled, tasks that exactly fill the time are all scheduled, and an owner with zero minutes gets an empty plan.
  - Empty task lists: an owner with no pets, or a pet with no tasks, gets an empty plan without errors.
  - Task selection: overdue tasks are included, and completed and future tasks are left out.
  - Order: the chosen tasks are listed in time order.

To check that the daily-plan tests are meaningful, each one was also run against deliberately broken versions of the scheduler (for example, one that ignores priority or the time limit), patched in memory only. Every broken version made at least one test fail.

### Confidence Level

**★★★★☆ (4/5 stars)**

The backend in `pawpal_system.py` is well tested: every scheduling feature has its own automated tests, including edge cases, and all 37 pass. I am not giving it 5 stars because the Streamlit interface (`app.py`) is not yet connected to the scheduling features. It cannot build a plan, sort, filter, complete recurring tasks, or show conflict warnings yet, and it has no automated tests. That part still needs full integration and testing.

## 📐 Smarter Scheduling

These features are implemented in the `Scheduler` and `Task` classes in `pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Chronological by `"HH:MM"`; tasks without a time go last |
| Filtering | `Scheduler.filter_tasks()` | By pet name, completion status, or both |
| Conflict handling | `Scheduler.detect_conflicts()` | Warns about exact-time and overlapping tasks on the same date |
| Recurring tasks | `Scheduler.complete_task()`, `Task.next_occurrence()` | Daily tasks repeat the next day, weekly tasks seven days later |
| Time validation | `Task.__post_init__()` | Rejects times that are not 24-hour `HH:MM` |

### Sorting tasks by time

`sort_by_time()` returns tasks in chronological order. It converts each time into minutes after midnight before comparing, so `"8:05"` correctly comes before `"20:00"`. Tasks without a scheduled time go at the end. `build_daily_plan()` uses it to display the final plan in time order.

The scheduler still uses the separate `sort_tasks()` method to decide *which* tasks fit in the owner's available time (by priority, preferred category, and time of day). `sort_by_time()` only changes the order in which the chosen tasks are shown.

Limitation: `sort_by_time()` looks only at the clock time, not the due date, so it is meant for a single day's tasks.

### Filtering tasks

`filter_tasks(pet_name=None, completed=None)` returns the owner's tasks across all pets, with optional filters:

```python
scheduler.filter_tasks(pet_name="luna")                    # all of Luna's tasks (case-insensitive)
scheduler.filter_tasks(completed=False)                    # every pending task
scheduler.filter_tasks(pet_name="Mochi", completed=True)   # Mochi's completed tasks
scheduler.filter_tasks()                                   # every task
```

### Recurring tasks

When a task is completed with `scheduler.complete_task(pet, task)`, the task is marked complete. If its `recurrence` is `"daily"` or `"weekly"`, a new incomplete copy is added to the pet:

- A daily task's next occurrence is due one day later. A weekly task's is due seven days later.
- The new task keeps the same title, pet, priority, duration, and scheduled time.
- If the task was overdue, the next date is counted from today, so the new task is not already in the past.
- Completing the same task again does not create a duplicate occurrence.
- Tasks with `recurrence="none"` (the default) do not repeat.

### Conflict warnings

`detect_conflicts()` returns a list of readable warning messages instead of raising errors. It compares every pair of tasks that have a scheduled time and are due on the same date, for the same pet or different pets. Each task takes up the time from its start until its start plus its duration, and two tasks conflict when those time ranges overlap:

- **Exact-time conflict:** two tasks start at the same time, for example both pets' breakfasts at 07:30.
- **Overlapping durations:** one task starts before another one ends, for example a 30-minute walk at 08:00 and a litter box task at 08:15.

A task that starts exactly when another one ends is not a conflict. The scheduler only warns about conflicts. It does not move tasks automatically, so the owner decides how to fix them. Tasks that cross midnight are not checked yet.

### Time validation

A task's `time` must be empty (no scheduled time) or a valid 24-hour time in `HH:MM` format, from `00:00` to `23:59`. Times like `"08:00"`, `"18:30"`, and `"8:05"` are accepted. Invalid times like `"8am"`, `"25:99"`, `"12:60"`, or `"hello"` raise a `ValueError` when the task is created:

```text
ValueError: Invalid time '8am' for task 'Morning walk': time must be in 24-hour HH:MM format (e.g. '08:00' or '18:30').
```

### Where each feature is available

The Smarter Scheduling features are currently available in the **backend and CLI demo only**. The Streamlit app has not been connected to them yet.

| Feature | Backend (`pawpal_system.py`) | CLI demo (`main.py`) | Streamlit app (`app.py`) |
|---------|:---:|:---:|:---:|
| Add pets | ✅ | ✅ | ✅ |
| Add tasks (title, duration, priority) | ✅ | ✅ | ✅ |
| Scheduled time, category, recurrence on tasks | ✅ | ✅ | ❌ no inputs yet |
| Build the daily plan | ✅ | ✅ | ❌ button is a placeholder |
| Sort by time | ✅ | ✅ | ❌ |
| Filter tasks | ✅ | ✅ | ❌ |
| Recurring tasks | ✅ | ✅ | ❌ |
| Conflict warnings | ✅ | ✅ | ❌ |
| Time validation | ✅ | ✅ checked on every task (no invalid example shown) | ❌ app tasks have no time field |

In the Streamlit app you can add pets and tasks and see them in tables, and it warns about duplicate pets and tasks. To see the scheduling features, run `python3 main.py`.

## 📸 Demo Walkthrough

The scheduling features are demonstrated in the CLI (the Streamlit app is not connected to them yet). Run `python3 main.py` and follow along:

1. **Sample data is created.** The owner, Jordan, has 90 minutes available and prefers walk and meds tasks. Jordan has two pets, Mochi (dog) and Luna (cat). Their eight tasks are added deliberately out of time order. Two of Luna's tasks are set up to cause conflicts: her Breakfast is at 07:30, the same time as Mochi's, and her Litter box task at 08:15 starts during Mochi's 08:00–08:30 walk.
2. **Today's schedule is built.** Before anything is marked complete, the scheduler chooses tasks by priority until the 90 minutes are used up and prints them in time order. The low-priority 45-minute "Bath and brush" is skipped because no time is left, and the reason is printed.
3. **Conflict warnings are printed.** Under the schedule, the CLI warns that both breakfasts are at 07:30 and that Mochi's walk overlaps Luna's litter box task.
4. **Tasks are sorted by time.** Section 2 prints all eight tasks in the order they were added, then again after `sort_by_time()`, from 07:30 to 18:00.
5. **Recurring tasks are completed.** Section 3 completes Mochi's daily Breakfast and weekly Nail trim using `complete_task()`. The CLI prints each new task: Breakfast is due tomorrow and Nail trim is due in seven days, both with the same scheduled time and marked as not completed.
6. **Tasks are filtered.** Section 4 shows `filter_tasks()` three ways: all of Luna's tasks (using the lowercase name `"luna"`), only completed tasks (the two just completed), and Mochi's pending tasks, which now include the new Breakfast and Nail trim occurrences.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
