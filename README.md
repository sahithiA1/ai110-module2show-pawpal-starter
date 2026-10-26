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

- **Task** is a single care activity, such as a walk, feeding, medication, or grooming. It stores the duration, priority, category, preferred time, due date, and whether the task repeats. It can mark itself complete and create its next occurrence (daily or weekly).
- **Pet** holds its own list of tasks. It can add tasks (ignoring duplicates), remove them, and return the ones still pending.
- **Owner** has a name, a daily time budget (`available_minutes`), preferred task categories, and one or more pets.
- **Scheduler** builds the daily plan for one owner. It sorts pending tasks by priority, preferred category, and time of day, then adds them until the owner's available minutes run out. It records why each task was scheduled or skipped, warns when two tasks share the same time, and adds the next occurrence when a recurring task is completed.

The Scheduler does not read tasks from a single pet. It gets them from `Owner.get_all_tasks()`, which combines the tasks of every pet the owner has, so one plan covers all of the owner's pets.

## 🖥️ Sample Output

Run the demo with `python main.py` to generate today's schedule for Jordan's pets, Mochi and Luna:

```text
============================================================
  Today's Schedule for Jordan  (2026-10-26)
============================================================
Time   Pet     Task                  Duration  Priority
------------------------------------------------------------
07:30  Mochi   Breakfast             10 min    high
08:00  Mochi   Morning walk          30 min    high
09:00  Luna    Thyroid medication    5 min     high
18:00  Luna    Dinner                10 min    medium
------------------------------------------------------------
Time used: 55 of 90 minutes

Skipped tasks:
  - Bath and brush for Mochi (low priority): needs 45 min, but only 35 min were left
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
python -m pytest --cov=pawpal_system
```

Coverage requires the `pytest-cov` package (`pip install pytest-cov`).

Sample test output:

```text
2 passed in 0.12s
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
