import streamlit as st

from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Age (years)", min_value=0, max_value=40, value=3)

# Create the Owner only once so its pets and tasks survive Streamlit reruns
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name, available_minutes=90)
owner = st.session_state.owner
owner.name = owner_name  # keep the stored owner in sync with the name input

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
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

task_pet_name = st.selectbox("Pet for this task", [p.name for p in owner.pets])

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    task_pet = next((p for p in owner.pets if p.name == task_pet_name), None)
    if task_pet is None:
        st.warning("Add a pet before adding tasks.")
    else:
        task_count = len(task_pet.tasks)
        task_pet.add_task(Task(task_title, int(duration), priority=priority))
        if len(task_pet.tasks) == task_count:  # add_task ignores duplicates
            st.warning(f"{task_pet.name} already has '{task_title}' today.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": t.pet_name,
                "title": t.title,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority,
            }
            for t in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
