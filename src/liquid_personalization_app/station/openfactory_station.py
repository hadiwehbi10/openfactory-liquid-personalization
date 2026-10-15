"""Real OpenFactory backend for the liquid personalization station."""

from __future__ import annotations

import os
from typing import Any

from openfactory.assets import Asset
from openfactory.kafka import KSQLDBClient

from liquid_personalization_app.station.base import StationState


class OpenFactoryStation:
    """Control and monitor the physical station through OpenFactory."""

    ASSET_UUID = "OPTA-LAB-001"

    def __init__(self, asset: Any | None = None) -> None:
        """Create the OpenFactory station adapter.

        An Asset object may be injected for testing. When one is not
        provided, the real OpenFactory asset is created.
        """

        if asset is not None:
            self._asset = asset
            return

        self._asset = Asset(
            self.ASSET_UUID,
            ksqlClient=KSQLDBClient(
                os.getenv(
                    "KSQLDB_URL",
                    "http://localhost:8088",
                )
            ),
            bootstrap_servers=os.getenv(
                "KAFKA_BROKER",
                "localhost:9092",
            ),
            asset_router_url=os.getenv(
                "ASSET_ROUTER_URL"
            ),
        )

    @staticmethod
    def _sensor_detected(raw_value: Any) -> bool:
        """Convert the physical active-low sensor signal.

        Physical sensor semantics:

            True  = clear
            False = bottle detected

        Playground semantics:

            True  = bottle detected
            False = clear
        """

        return not OpenFactoryStation._read_bool(raw_value)

    @staticmethod
    def _read_bool(attribute: Any) -> bool:
        value = getattr(attribute, "value", attribute)
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().lower() in ("true", "false"):
            return value.strip().lower() == "true"
        raise ValueError(f"Unexpected boolean value: {value!r}")

    def _ensure_available(self) -> None:
        """Refuse actuator activation unless OpenFactory reports OPTA available."""
        attr = getattr(self._asset, "avail", None)
        value = getattr(attr, "value", attr)
        if not isinstance(value, str) or value.strip().upper() != "AVAILABLE":
            raise RuntimeError("OPTA not AVAILABLE: actuator command refused")

    def get_state(self) -> StationState:
        """Read and normalize the current OpenFactory station state."""

        availability_attr = getattr(self._asset, "avail", None)
        availability_value = getattr(availability_attr, "value", availability_attr)

        return {
            "opta_availability": str(availability_value or "UNKNOWN").strip().upper(),
            "sensor1_detected": self._sensor_detected(
                self._asset.digital_input_i1
            ),
            "sensor2_detected": self._sensor_detected(
                self._asset.digital_input_i2
            ),
            "conveyor_running": self._read_bool(
                self._asset.relay_2
            ),
            "stopper_engaged": self._read_bool(
                self._asset.relay_4
            ),
        }

    def start_conveyor(self) -> StationState:
        """Start the real conveyor through OpenFactory."""

        self._ensure_available()
        self._asset.relay_2 = True

        return self.get_state()

    def stop_conveyor(self) -> StationState:
        """Stop the real conveyor through OpenFactory."""

        self._asset.relay_2 = False

        return self.get_state()

    def engage_stopper(self) -> StationState:
        """Engage the real bottle stopper through OpenFactory."""

        self._ensure_available()
        self._asset.relay_4 = True

        return self.get_state()

    def release_stopper(self) -> StationState:
        """Release the real bottle stopper through OpenFactory."""

        self._asset.relay_4 = False

        return self.get_state()

    def close(self) -> None:
        """Close the underlying OpenFactory asset connection."""

        close_method = getattr(
            self._asset,
            "close",
            None,
        )

        if callable(close_method):
            close_method()