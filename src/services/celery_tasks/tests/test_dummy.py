from services.celery_tasks.dummy import dummy_task


def test_dummy_task_runs_and_returns_none() -> None:
    assert dummy_task() is None


def test_dummy_task_is_registered_under_expected_name() -> None:
    assert dummy_task.name == "dummy.dummy_task"
