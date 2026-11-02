
"""Common interface for the real and simulated factory stations.

The website uses the same functions for both stations.
The real station communicates through OpenFactory, while the
simulator updates values in memory.

Reported equipment states do not guarantee physical movement.
"""

from __future__ import annotations

from typing import NotRequired, Protocol, TypedDict


class StationState(TypedDict):
    """Station information displayed in the Playground.

    Sensor values are True when a bottle is detected, even
    though the physical sensors use active-low signals.

    In real mode, relay values come from OpenFactory and may
    be outdated if communication is lost.
    """

    sensor1_detected: bool
    sensor2_detected: bool
    conveyor_running: bool
    stopper_engaged: bool
    opta_availability: NotRequired[str]


class StationBackend(Protocol):
    """Functions that both station types must provide.

    Commands request an action but do not confirm that
    the physical equipment actually moved.
    """

    def get_state(self) -> StationState:
        """Return the station's reported state."""
        ...

    def start_conveyor(self) -> StationState:
        """Request to start the conveyor."""
        ...

    def stop_conveyor(self) -> StationState:
        """Request to stop the conveyor.

        This is not a guaranteed physical emergency stop.
        """
        ...

    def engage_stopper(self) -> StationState:
        """Request to engage the bottle stopper."""
        ...

    def release_stopper(self) -> StationState:
        """Request to release the bottle stopper."""
        ...
