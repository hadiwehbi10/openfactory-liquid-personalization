
"""OpenFactory adapter for the physical liquid-personalization station.

Control path:
    Flask API -> OpenFactory Asset -> OpenFactory infrastructure
    -> OPC UA gateway -> Arduino OPTA -> physical relay output

Observation path:
    Physical sensor -> Arduino OPTA -> OPC UA gateway
    -> OpenFactory Asset -> Flask API

The Arduino OPTA is responsible for physical I/O execution.

This adapter provides supervisory command requests and state
observations. It does not independently verify actuator motion,
implement a local safety watchdog, or guarantee data freshness.
"""

from __future__ import annotations

import os
from typing import Any

from openfactory.assets import Asset
from openfactory.kafka import KSQLDBClient

from liquid_personalization_app.station.base import StationState


class OpenFactoryStation:
    """Communicate with the physical station through OpenFactory.

    The station is represented by the OPTA-LAB-001 asset.

    Relay commands are submitted through the OpenFactory SDK.
    Sensor and relay attributes are retrieved through the same SDK.

    Reported values must not be confused with independently
    verified physical equipment states.
    """

    ASSET_UUID = "OPTA-LAB-001"

    def __init__(self, asset: Any | None = None) -> None:
        """Initialize the OpenFactory station adapter.

        Args:
            asset: Optional OpenFactory-compatible asset object.
                A fake asset can be injected for unit testing.

        The real implementation connects to OpenFactory services
        using environment-provided configuration.
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
        """Convert an active-low sensor reading to detection state.

        The laboratory photoelectric sensors use:

            HIGH / True  -> no bottle detected
            LOW / False  -> bottle detected

        The dashboard expects the opposite logical representation:

            True  -> bottle detected
            False -> no bottle detected

        This method only converts the signal. It does not
        validate whether the reading is recent.
        """
        return not OpenFactoryStation._read_bool(raw_value)

    @staticmethod
    def _read_bool(attribute: Any) -> bool:
        """Normalize a boolean value returned by OpenFactory.

        OpenFactory attributes may expose their value through
        a .value property. Test doubles can provide plain values.

        Unexpected representations raise ValueError rather
        than silently producing an incorrect equipment state.
        """
        value = getattr(attribute, "value", attribute)

        if isinstance(value, bool):
            return value

        if (
            isinstance(value, str)
            and value.strip().lower() in ("true", "false")
        ):
            return value.strip().lower() == "true"

        raise ValueError(
            f"Unexpected boolean value: {value!r}"
        )

    def _ensure_available(self) -> None:
        """Block activation when OpenFactory reports OPTA unavailable.

        This is a supervisory software interlock used before
        issuing a new activation request.

        It is NOT a physical safety interlock or a local watchdog.
        Availability may change after the check, and AVAILABLE
        does not independently prove the device is responsive.
        """
        attr = getattr(self._asset, "avail", None)
        value = getattr(attr, "value", attr)

        if (
            not isinstance(value, str)
            or value.strip().upper() != "AVAILABLE"
        ):
            raise RuntimeError(
                "OPTA not AVAILABLE: actuator command refused"
            )

    def get_state(self) -> StationState:
        """Return the station state reported through OpenFactory.

        Returns:
            Normalized sensor readings, relay states, and the
            reported OPTA availability.

        Important:
            Relay values indicate OpenFactory-reported output
            state, not independently measured actuator behavior.

            Values may be cached or delayed during communication
            failures. Consumers must account for availability
            and should not assume guaranteed data freshness.
        """
        availability_attr = getattr(
            self._asset,
            "avail",
            None,
        )

        availability_value = getattr(
            availability_attr,
            "value",
            availability_attr,
        )

        return {
            "opta_availability": str(
                availability_value or "UNKNOWN"
            ).strip().upper(),

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
        """Request conveyor activation through OpenFactory.

        The activation request is rejected unless OpenFactory
        currently reports OPTA availability as AVAILABLE.

        Returning a station state does not confirm physical
        conveyor movement.
        """
        self._ensure_available()

        self._asset.relay_2 = True

        return self.get_state()

    def stop_conveyor(self) -> StationState:
        """Request conveyor deactivation through OpenFactory.

        This operation remains callable even when the OPTA is
        reported unavailable.

        The command may still fail to reach the controller.
        It must not be treated as a guaranteed emergency stop.
        """
        self._asset.relay_2 = False

        return self.get_state()

    def engage_stopper(self) -> StationState:
        """Request bottle-stopper engagement through OpenFactory.

        Activation is rejected unless OpenFactory currently
        reports OPTA availability as AVAILABLE.

        Actual stopper movement is not independently verified.
        """
        self._ensure_available()

        self._asset.relay_4 = True

        return self.get_state()

    def release_stopper(self) -> StationState:
        """Request bottle-stopper release through OpenFactory.

        The request remains callable if the OPTA is reported
        unavailable, but delivery and physical movement are
        not guaranteed.
        """
        self._asset.relay_4 = False

        return self.get_state()

    def close(self) -> None:
        """Close the OpenFactory asset if it supports cleanup.

        Injected test assets may not implement close().
        """
        close_method = getattr(
            self._asset,
            "close",
            None,
        )

        if callable(close_method):
            close_method()
