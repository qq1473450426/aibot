from app.core.models import WorkerState
from app.core.state_machine import transition

def test_valid():assert transition(WorkerState.IDLE,WorkerState.RUNNING)==WorkerState.RUNNING

def test_invalid():
    try:transition(WorkerState.STOPPED,WorkerState.BATTLE)
    except ValueError:return
    assert False
