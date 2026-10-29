from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption(
    "A pet care planner that builds a daily schedule for your pets "
    "based on your available time and each task's priority."
)

st.divider()

st.subheader("Owner & Pets")

# Create the Owner only once so its pets and tasks survive Streamlit reruns
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=90)
owner = st.session_state.owner

owner_col, minutes_col = st.columns(2)
with owner_col:
    owner_name = st.text_input("Owner name", value="Jordan")
with minutes_col:
    available_minutes = st.number_input(
        "Available minutes today", min_value=0, max_value=1440, value=90, step=5,
        key="available_minutes",
    )
# Keep the stored owner in sync with the inputs
owner.name = owner_name
owner.available_minutes = int(available_minutes)

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Age (years)", min_value=0, max_value=40, value=3)

if st.button("Add pet"):
    try:
        owner.add_pet(Pet(pet_name, species=species, age=int(age)))
        st.success(f"Added {pet_name} the {species}.")
    except ValueError as error:  # add_pet rejects a duplicate pet name
        st.warning(str(error))

if owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {"name": p.name, "species": p.species, "age": p.age, "tasks": len(p.tasks)}
            for p in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")

task_pet_name = st.selectbox("Pet for this task", [p.name for p in owner.pets])

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns(3)
with col4:
    category = st.selectbox(
        "Category", ["walk", "feeding", "meds", "grooming", "other"], key="task_category"
    )
with col5:
    preferred_time = st.selectbox(
        "Preferred time", ["any", "morning", "afternoon", "evening"], key="task_preferred_time"
    )
with col6:
    recurrence = st.selectbox("Repeats", ["none", "daily", "weekly"], key="task_recurrence")

time_col1, time_col2 = st.columns(2)
with time_col1:
    has_time = st.checkbox("Set a specific time", key="task_has_time")
with time_col2:
    scheduled_time = st.time_input(
        "Scheduled time", value=time(8, 0), step=300, disabled=not has_time, key="task_time"
    )

if st.button("Add task"):
    task_pet = next((p for p in owner.pets if p.name == task_pet_name), None)
    if task_pet is None:
        st.warning("Add a pet before adding tasks.")
    else:
        try:
            task = Task(
                task_title,
                int(duration),
                priority=priority,
                category=category,
                preferred_time=preferred_time,
                time=scheduled_time.strftime("%H:%M") if has_time else "",
                recurrence=recurrence,
            )
        except ValueError as error:  # Task rejects a time that is not 24-hour HH:MM
            st.warning(str(error))
        else:
            task_count = len(task_pet.tasks)
            task_pet.add_task(task)
            if len(task_pet.tasks) == task_count:  # add_task ignores duplicates
                st.warning(f"{task_pet.name} already has '{task_title}' at that time today.")

st.markdown("#### All Tasks")
if owner.get_all_tasks():
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        pet_filter = st.selectbox(
            "Pet", ["All pets"] + [p.name for p in owner.pets], key="filter_pet"
        )
    with filter_col2:
        status_filter = st.radio(
            "Status", ["All", "Pending", "Completed"], horizontal=True, key="filter_status"
        )
    with filter_col3:
        sort_by_time = st.checkbox("Sort by scheduled time", value=True, key="sort_by_time")

    # Filtering and sorting are done by the Scheduler; None means "don't filter"
    task_view = Scheduler(owner)
    shown_tasks = task_view.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "Pending": False, "Completed": True}[status_filter],
    )
    if sort_by_time:
        shown_tasks = task_view.sort_by_time(shown_tasks)

    if shown_tasks:
        st.dataframe(
            [
                {
                    "Pet": t.pet_name,
                    "Task": t.title,
                    "Time": t.time or "—",
                    "Due Date": t.due_date.isoformat(),
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Category": t.category,
                    "Preferred Time": t.preferred_time,
                    "Repeats": t.recurrence,
                    "Status": "Completed" if t.completed else "Pending",
                }
                for t in shown_tasks
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No tasks match the selected filters. Try choosing a different pet or status.")
else:
    st.info("No tasks yet. Add one above.")

st.markdown("#### Complete a Task")

# Show the result of the last completion, saved before the rerun below
if "completion_message" in st.session_state:
    st.success(st.session_state.pop("completion_message"))

completion_view = Scheduler(owner)
pending_tasks = completion_view.sort_by_time(completion_view.filter_tasks(completed=False))
if pending_tasks:
    # Choose by position so the selected task is always the real object from this run's pending list
    selected_index = st.selectbox(
        "Pending task",
        range(len(pending_tasks)),
        format_func=lambda i: (
            f"{pending_tasks[i].pet_name} – {pending_tasks[i].title} "
            f"({pending_tasks[i].time or 'no time'}, due {pending_tasks[i].due_date.isoformat()})"
        ),
        key="task_to_complete",
    )
    task_to_complete = pending_tasks[selected_index]
    if st.button("Mark Complete", key="mark_complete"):
        task_pet = next(p for p in owner.pets if p.name == task_to_complete.pet_name)
        next_task = completion_view.complete_task(task_pet, task_to_complete)
        if next_task is None:
            message = f"Completed '{task_to_complete.title}' for {task_pet.name}."
        else:
            message = (
                f"Completed '{task_to_complete.title}' for {task_pet.name}. "
                f"It repeats {task_to_complete.recurrence}, so the next one is due "
                f"{next_task.due_date.isoformat()}" + (f" at {next_task.time}." if next_task.time else ".")
            )
        st.session_state.completion_message = message
        # Rerun so the All Tasks table above and the schedule below show the updated tasks
        st.rerun()
else:
    st.info("There are no pending tasks to complete.")

st.divider()

st.subheader("Build Schedule")
st.caption("Tasks are chosen by priority until your available minutes run out, then listed in time order.")

# A button is only True on the rerun right after a click, so remember that the plan should stay visible
if st.button("Generate schedule"):
    st.session_state.show_plan = True

if st.session_state.get("show_plan"):
    # Rebuild from the current owner data on every rerun so the plan never goes stale
    scheduler = Scheduler(owner)
    scheduler.build_daily_plan()

    if not scheduler.scheduled_tasks and not scheduler.skipped_tasks:
        st.info("There are no pending tasks to schedule today. Add a pet and a task above.")
    else:
        used_col, scheduled_col, skipped_col = st.columns(3)
        used_col.metric(
            "Minutes used", f"{scheduler.total_scheduled_minutes()} / {owner.available_minutes}"
        )
        scheduled_col.metric("Tasks scheduled", len(scheduler.scheduled_tasks))
        skipped_col.metric("Tasks skipped", len(scheduler.skipped_tasks))

        st.markdown(f"#### Today's schedule ({scheduler.plan_date.isoformat()})")
        if scheduler.scheduled_tasks:
            st.dataframe(
                [
                    {
                        "Time": t.time or "—",
                        "Pet": t.pet_name,
                        "Task": t.title,
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority,
                    }
                    for t in scheduler.scheduled_tasks  # already in time order
                ],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No tasks fit in your available time today.")

        st.markdown("#### Skipped tasks")
        if scheduler.skipped_tasks:
            st.caption("These tasks did not fit in the time that was left.")
            st.dataframe(
                [
                    {
                        "Pet": t.pet_name,
                        "Task": t.title,
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority,
                    }
                    for t in scheduler.skipped_tasks
                ],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.success("Everything fit in today's plan.")

        st.markdown("#### Scheduling Conflicts")
        # Only check the plan itself; with an empty plan, detect_conflicts() would fall back to
        # pending tasks and warn about tasks that are not scheduled today.
        conflicts = scheduler.detect_conflicts() if scheduler.scheduled_tasks else []
        if conflicts:
            st.caption("These scheduled tasks overlap. Adjust a time or duration to resolve them.")
            for warning in conflicts:
                st.warning(warning, icon="⚠️")
        else:
            st.success("No scheduling conflicts detected.")
