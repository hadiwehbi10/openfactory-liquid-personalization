"""Simulation backend for the liquid personalization station."""

from __future__ import annotations

from threading import Lock

from liquid_personalization_app.station.base import StationState


class StationSimulator:
    """Maintain the simulated state of the factory station."""

    def __init__(self) -> None:
        self._lock = Lock()

        self.sensor1_detected = False
        self.sensor2_detected = False

        self.conveyor_running = False
        self.stopper_engaged = False

    def get_state(self) -> StationState:
        """Return the current simulated station state."""

        with self._lock:
            return {
                "sensor1_detected": self.sensor1_detected,
                "sensor2_detected": self.sensor2_detected,
                "conveyor_running": self.conveyor_running,
                "stopper_engaged": self.stopper_engaged,
            }

    def start_conveyor(self) -> StationState:
        """Start the simulated conveyor."""

        with self._lock:
            self.conveyor_running = True

        return self.get_state()

    def stop_conveyor(self) -> StationState:
        """Stop the simulated conveyor."""

        with self._lock:
            self.conveyor_running = False

        return self.get_state()

    def engage_stopper(self) -> StationState:
        """Engage the simulated bottle stopper."""

        with self._lock:
            self.stopper_engaged = True

        return self.get_state()

    def release_stopper(self) -> StationState:
        """Release the simulated bottle stopper."""

        with self._lock:
            self.stopper_engaged = False

        return self.get_state()