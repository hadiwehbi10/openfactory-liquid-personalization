"""Simulation backend for the liquid personalization station."""

from __future__ import annotations

from threading import Lock


class StationSimulator:
    """Maintain the simulated state of the factory station."""

    def __init__(self) -> None:
        self._lock = Lock()

        self.sensor1_detected = False
        self.sensor2_detected = False
        self.conveyor_running = False
        self.stopper_engaged = False

    def get_state(self) -> dict[str, bool]:
        """Return the current simulated station state."""
        with self._lock:
            return {
                "sensor1_detected": self.sensor1_detected,
                "sensor2_detected": self.sensor2_detected,
                "conveyor_running": self.conveyor_running,
                "stopper_engaged": self.stopper_engaged,
            }

    def start_conveyor(self) -> dict[str, bool]:
        """Start the simulated conveyor."""
        with self._lock:
            self.conveyor_running = True

        return self.get_state()

    def stop_conveyor(self) -> dict[str, bool]:
        """Stop the simulated conveyor."""
        with self._lock:
            self.conveyor_running = False

        return self.get_state()

    def engage_stopper(self) -> dict[str, bool]:
        """Engage the simulated stopper."""
        with self._lock:
            self.stopper_engaged = True

        return self.get_state()

    def release_stopper(self) -> dict[str, bool]:
        """Release the simulated stopper."""
        with self._lock:
            self.stopper_engaged = False

        return self.get_state()


station_simulator = StationSimulator()