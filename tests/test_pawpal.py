"""Basic tests for the PawPal+ Task and Pet classes."""

from pawpal_system import Pet, Task


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
