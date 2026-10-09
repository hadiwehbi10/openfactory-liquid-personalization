"""Common interface for liquid personalization station backends."""

from __future__ import annotations

from typing import Protocol, TypedDict


class StationState(TypedDict):
    """Normalized state exposed to the playground."""

    sensor1_detected: bool
    sensor2_detected: bool
    conveyor_running: bool
    stopper_engaged: bool


class StationBackend(Protocol):
    """Interface implemented by simulation and real station backends."""

    def get_state(self) -> StationState:
        """Return the current normalized station state."""
        ...

    def start_conveyor(self) -> StationState:
        """Start the conveyor and return the resulting state."""
        ...

    def stop_conveyor(self) -> StationState:
        """Stop the conveyor and return the resulting state."""
        ...

    def engage_stopper(self) -> StationState:
        """Engage the bottle stopper and return the resulting state."""
        ...

    def release_stopper(self) -> StationState:
        """Release the bottle stopper and return the resulting state."""
        ...