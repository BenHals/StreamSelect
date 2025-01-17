from typing import Dict, Optional

from river.base import DriftDetector
from river.base.typing import ClfTarget

# from river.drift import ADWIN, DDM, EDDM


class Observation:
    """A container class for a stored observation."""

    def __init__(
        self, x: dict, y: Optional[ClfTarget], seen_at: float, active_state_id: int, sample_weight: float = 1.0
    ) -> None:
        self.x = x
        self.y = y
        self.seen_at = seen_at
        self.active_state_id = active_state_id
        self.sample_weight = sample_weight
        # A mappting between state_ids and their predictions for this observation.
        self.predictions: Dict[int, ClfTarget] = {}

        # The relevance calculated to the active state when first observed.
        self.active_state_relevance: Optional[float] = None

        # Whether or not the observation is stable to train on.
        self.is_stable = False

    def add_prediction(self, p: ClfTarget, state_id: int) -> None:
        """Add a prediction to the observation for the state with the given state_id."""
        self.predictions[state_id] = p

    def add_active_state_relevance(self, active_state_relevance: float, active_state_id: int) -> None:
        """Add the relevance calculated to the active state when this observation is the most
        recently observed observation. Pass active_state_id to confirm the correct state."""
        if active_state_id != self.active_state_id:
            raise ValueError(f"Attempting to set active state relevance for wrong state {active_state_id}.")

        self.active_state_relevance = active_state_relevance

    def __str__(self) -> str:
        return f"<{self.x}|{self.y}|{self.seen_at}>"

    def __repr__(self) -> str:
        return str(self)


def get_drift_detector_estimate(detector: DriftDetector) -> float:
    """Extract the mean estimate of a drift detector."""
    if hasattr(detector, "estimation"):
        return detector.estimation  # type: ignore

    raise ValueError("Cannot get estimate from detector. Either use a different detector or use the 'any' mode. ")
