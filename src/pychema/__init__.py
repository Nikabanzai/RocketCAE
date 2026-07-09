"""PyCHEMA: preliminary liquid rocket engine trade studies via NASA CEA."""

from pychema.models import EngineInputs, EngineResult, SweepResult
from pychema.cea_runner import run_rocket
from pychema.propellants import list_propellant_pairs, get_pair

__all__ = [
    "EngineInputs",
    "EngineResult",
    "SweepResult",
    "run_rocket",
    "list_propellant_pairs",
    "get_pair",
]

__version__ = "0.2.0"
