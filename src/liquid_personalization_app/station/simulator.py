
"""Simulate the factory station without using physical equipment.

The simulator stores sensor, conveyor, and stopper states in memory.
It allows us to develop and test the application without connecting
to OpenFactory or the Arduino OPTA.
"""

from __future__ import annotations

from threading import Lock

from liquid_personalization_app.station.base import StationState


class StationSimulator:
    """Manage the simulated sensors, conveyor, and stopper."""

    def __init__(self) -> None:
        """Initialize the station with all equipment inactive."""

        # Prevent multiple requests from changing the state at the same time.
        self._lock = Lock()

        # Both sensors start with no bottle detected.
        self.sensor1_detected = False
        self.sensor2_detected = False

        # The conveyor and stopper start inactive.
        self.conveyor_running = False
        self.stopper_engaged = False

    def get_state(self) -> StationState:
        """Return a copy of the current simulated station state."""

        with self._lock:
            return {
                "sensor1_detected": self.sensor1_detected,
                "sensor2_detected": self.sensor2_detected,
                "conveyor_running": self.conveyor_running,
                "stopper_engaged": self.stopper_engaged,
            }

    def start_conveyor(self) -> StationState:
        """Set the simulated conveyor to running."""

        with self._lock:
            self.conveyor_running = True

        return self.get_state()

    def stop_conveyor(self) -> StationState:
        """Set the simulated conveyor to stopped."""

        with self._lock:
            self.conveyor_running = False

        return self.get_state()

    def engage_stopper(self) -> StationState:
        """Set the simulated stopper to engaged."""

        with self._lock:
            self.stopper_engaged = True

        return self.get_state()

    def release_stopper(self) -> StationState:
        """Set the simulated stopper to released."""

        with self._lock:
            self.stopper_engaged = False

        return self.get_state()
