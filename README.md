# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan daily care tasks for their pets. It was built for the CodePath AI110 Module 2 project. The scheduling logic lives in a tested Python backend (`pawpal_system.py`), and the Streamlit interface (`app.py`) is fully connected to it: you can add pets and tasks, generate a daily schedule, see conflict warnings, filter and sort tasks, and complete tasks that repeat daily or weekly.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

The project was built by designing the system first (UML), then implementing the logic in Python, then connecting it to the Streamlit UI.

## What you will build

The assignment asks for an app that can:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

PawPal+ covers these, with one limit: tasks can be added and marked complete in the app, but not edited or deleted after they are created.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the Streamlit app

```bash
streamlit run app.py
```

Streamlit opens the app in your browser (usually at http://localhost:8501). Pets and tasks are kept while the app is open, but they are not saved to a file, so refreshing the page starts over.

### Run the CLI demo

```bash
python3 main.py
```

### Run the tests

```bash
python3 -m pytest
```

See [Testing PawPal+](#testing-pawpal) for details.

### Suggested workflow

These are the steps from the assignment that this project followed:

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Using the Streamlit App

The app is one page with four parts.

### Owner & Pets

- Enter the **owner name** and **available minutes today** (starts at 90). The available minutes are the time budget the scheduler fills.
- Add a pet with a **name**, **species** (dog, cat, or other), and **age**. Pet names must be unique; adding a duplicate shows a warning.
- The pets table shows each pet and how many tasks it has.

### Tasks

Choose a pet and fill in the task form:

| Field | Options |
|-------|---------|
| Task title | Any text |
| Duration (minutes) | 1–240 |
| Priority | low, medium, high |
| Category | walk, feeding, meds, grooming, other |
| Preferred time | any, morning, afternoon, evening |
| Repeats | none, daily, weekly |
| Scheduled time | Optional: tick **Set a specific time** and pick a time; otherwise the task has no set time |

New tasks are due today. Adding the same task for the same pet at the same time twice shows a warning instead of creating a duplicate.

### All Tasks

A table of every task with its pet, time, due date, duration, priority, category, preferred time, repeat setting, and status. Three controls change what it shows:

- **Pet:** "All pets" or one pet.
- **Status:** All, Pending, or Completed.
- **Sort by scheduled time:** on by default. Tasks are listed by time, with untimed tasks at the end. When it is off, tasks are listed pet by pet in the order they were added.

If nothing matches the filters, the app says so instead of showing an empty table. The filtering and sorting are done by the backend's `filter_tasks()` and `sort_by_time()` methods.

### Complete a Task

Pick a pending task from the list (each option shows the pet, task, time, and due date) and click **Mark Complete**.

- A one-time task is marked completed.
- A **daily** or **weekly** task is marked completed, and its next occurrence is created automatically. The confirmation message shows the new due date, for example: *"Completed 'Breakfast' for Mochi. It repeats daily, so the next one is due 2026-10-30 at 07:30."*

Completed tasks move to the Completed filter and leave today's schedule. The new occurrence appears as a pending task with its future due date.

### Build Schedule

Click **Generate schedule** to build today's plan. Once generated, the plan stays on the page and updates automatically when you add tasks, complete tasks, or change your available minutes.

- **Summary metrics:** minutes used (for example "55 / 90"), tasks scheduled, and tasks skipped.
- **Today's schedule:** the chosen tasks in time order.
- **Skipped tasks:** tasks that did not fit in the remaining time, or a message that everything fit.
- **Scheduling Conflicts:** one warning for each pair of scheduled tasks whose times overlap, such as *"'Morning walk' (Mochi, 08:00, 30 min) overlaps 'Litter box' (Luna, 08:15) on 2026-10-29"*, or "No scheduling conflicts detected." The app only warns; it does not move or delete tasks.

## Implementation Summary

The core logic lives in `pawpal_system.py` and is built from four classes:

- **Task** is a single care activity, such as a walk, feeding, medication, or grooming. It stores the duration, priority, category, preferred time, an optional scheduled time (`"HH:MM"`), due date, and whether the task repeats. It checks that its scheduled time is valid when it is created, can mark itself complete, and can create its next occurrence (daily or weekly).
- **Pet** holds its own list of tasks. It can add tasks (ignoring duplicates), remove them, and return the ones still pending.
- **Owner** has a name, a daily time budget (`available_minutes`), preferred task categories, and one or more pets.
- **Scheduler** builds the daily plan for one owner. It chooses tasks by priority, preferred category, and time of day, adding them until the owner's available minutes run out, and then displays the chosen tasks in chronological order. It records why each task was scheduled or skipped, warns about overlapping tasks, filters tasks, and adds the next occurrence when a recurring task is completed. See [Smarter Scheduling](#-smarter-scheduling) for details.

The Scheduler does not read tasks from a single pet. It gets them from `Owner.get_all_tasks()`, which combines the tasks of every pet the owner has, so one plan covers all of the owner's pets.

`app.py` keeps the `Owner` in `st.session_state` so pets and tasks survive Streamlit reruns, and creates a fresh `Scheduler` from it whenever it needs one. All scheduling, sorting, filtering, conflict detection, and recurrence logic comes from the backend; the app only collects input and displays results.

The class diagram is in `diagrams/uml.mmd`.

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
- `complete_task()` only accepts the pet's actual task object. A separate `Task` with the same field values raises a `ValueError`, so a copy can never be marked complete by mistake.

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

In the Streamlit app, times come from a time picker, so an invalid time cannot be entered there.

### Where each feature is available

| Feature | Backend (`pawpal_system.py`) | CLI demo (`main.py`) | Streamlit app (`app.py`) |
|---------|:---:|:---:|:---:|
| Add pets | ✅ | ✅ | ✅ |
| Add tasks (title, duration, priority) | ✅ | ✅ | ✅ |
| Scheduled time, category, preferred time, recurrence | ✅ | ✅ | ✅ |
| Available minutes | ✅ | ✅ (fixed at 90) | ✅ editable |
| Build the daily plan | ✅ | ✅ | ✅ |
| Sort by time | ✅ | ✅ | ✅ |
| Filter by pet and status | ✅ | ✅ | ✅ |
| Complete tasks and recurrence | ✅ | ✅ | ✅ |
| Conflict warnings | ✅ | ✅ | ✅ |
| Time validation | ✅ | ✅ | ✅ (time picker) |
| Owner preferred categories | ✅ | ✅ | ❌ not editable in the app |
| Edit or delete pets and tasks | ✅ remove methods | ❌ | ❌ |
| Explanation for each scheduled task (`explain_plan()`) | ✅ | ❌ (skipped reasons only) | ❌ |

## 🖥️ CLI Demo

`main.py` runs the backend without the UI. It creates an owner, Jordan, with 90 available minutes and two pets, Mochi and Luna, with eight tasks added out of time order. Two of the tasks are set up to conflict with others.

```bash
python3 main.py
```

The output has four sections: today's schedule (with skipped tasks and conflict warnings), sorting by time, recurring tasks, and filtering. Here are the first and third sections (dates depend on the day you run it):

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
collected 38 items

tests/test_pawpal.py ......................................              [100%]

============================== 38 passed in 0.09s ==============================
```

### What the tests cover

The 38 tests in `tests/test_pawpal.py` cover:

- **Task creation and completion:** marking a task complete and adding a task to a pet.
- **Sorting:** out-of-order times (including `"8:05"` vs `"20:00"`), untimed tasks going last, and leaving the original list unchanged.
- **Filtering:** case-insensitive pet names, completed and pending tasks, both filters combined, an unknown pet name, and no filters.
- **Recurring tasks:** daily and weekly next occurrences, non-recurring tasks, keeping task details, avoiding duplicates, overdue tasks, and rejecting a copied task that is not the pet's actual task.
- **Conflict detection:** exact-time conflicts, overlapping durations for the same pet and for different pets, and cases that should not be flagged (different dates, back-to-back tasks, and tasks without a time).
- **Time validation:** valid times, an empty time, and invalid times.
- **Daily plan (`build_daily_plan()`):**
  - Scheduling priorities: high-priority tasks are kept over low-priority ones.
  - Available-minute limits: the plan never goes over the owner's time, a task that does not fit is skipped while smaller tasks still get scheduled, tasks that exactly fill the time are all scheduled, and an owner with zero minutes gets an empty plan.
  - Empty task lists: an owner with no pets, or a pet with no tasks, gets an empty plan without errors.
  - Task selection: overdue tasks are included, and completed and future tasks are left out.
  - Order: the chosen tasks are listed in time order.

To check that the daily-plan tests are meaningful, each one was also run against deliberately broken versions of the scheduler (for example, one that ignores priority or the time limit), patched in memory only. Every broken version made at least one test fail. The copied-task test was also confirmed to fail against the old version of `complete_task()`.

The Streamlit app was checked during development with Streamlit's `AppTest` tool (adding tasks, generating schedules, conflict warnings, filters, and completing daily and weekly tasks). Those checks are not part of the saved test suite.

### Confidence Level

**★★★★☆ (4/5 stars)**

The backend in `pawpal_system.py` is well tested: every scheduling feature has its own automated tests, including edge cases, and all 38 pass. The Streamlit app is now fully connected to these features and was checked with `AppTest` while it was built. I am not giving it 5 stars because the app has no automated tests in the repository, and a few limitations remain: tasks that cross midnight are not checked for conflicts, `sort_by_time()` ignores the due date, and data is lost when the page is refreshed.

## 📸 Demo Walkthrough

This walkthrough follows one owner from adding a pet to completing a recurring task in the Streamlit app. Start it with `streamlit run app.py`.

1. **Set up the owner.** Enter an owner name, such as Jordan, and keep **Available minutes today** at 90.
2. **Add two pets.** Add Mochi (dog, 3) and then Luna (cat, 5). Both appear in the pets table.
3. **Add a timed, repeating task.** Choose Mochi, enter "Morning walk", 30 minutes, high priority, category walk, preferred time morning, Repeats **daily**. Tick **Set a specific time**, pick 08:00, and click **Add task**.
4. **Add a task that overlaps it.** Choose Luna, enter "Litter box", 10 minutes, medium priority, Repeats none, set the time to 08:15, and add it. It starts while Mochi's walk is still going.
5. **Add an untimed task.** Choose Mochi, enter "Play", 15 minutes, low priority, leave **Set a specific time** unticked, and add it.
6. **Look at All Tasks.** With **Sort by scheduled time** on, the list reads 08:00, 08:15, then Play (no time) at the end. Set **Pet** to Luna to see only her task, then set it back to All pets.
7. **Generate the schedule.** Click **Generate schedule**. The metrics show 55 / 90 minutes used, 3 tasks scheduled, and 0 skipped. Under **Scheduling Conflicts**, a warning says Mochi's 08:00 walk overlaps Luna's 08:15 litter box task.
8. **Try a smaller time budget.** Change **Available minutes today** to 40. The plan updates right away: the low-priority Play task moves to **Skipped tasks**, and the conflict warning is still shown.
9. **Complete the recurring task.** In **Complete a Task**, choose "Mochi – Morning walk (08:00, due …)" and click **Mark Complete**. The message confirms that it repeats daily and shows tomorrow's due date.
10. **Check the results.** In All Tasks, set **Status** to Completed to see today's walk, then Pending to see tomorrow's new walk. In the schedule, the walk is gone from today's plan, so the conflict warning is replaced by "No scheduling conflicts detected."

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
