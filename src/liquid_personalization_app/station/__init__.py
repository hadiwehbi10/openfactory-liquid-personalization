
"""Select the real or simulated factory station.

The station type is chosen using the STATION_MODE setting:
    - simulation: Use a simulated station (default).
    - real: Connect to the physical station through OpenFactory.

The selected station is created once and reused by the application.
"""

from __future__ import annotations

import os

from liquid_personalization_app.station.base import StationBackend
from liquid_personalization_app.station.simulator import StationSimulator


_station_backend: StationBackend | None = None


def get_station_backend() -> StationBackend:
    """Return the station selected by STATION_MODE.

    Simulation is the default so the application can run
    without connecting to physical equipment.

    Raises:
        ValueError: If STATION_MODE is not supported.
    """

    global _station_backend

    # Reuse the existing station instead of creating a new one.
    if _station_backend is not None:
        return _station_backend

    mode = os.getenv(
        "STATION_MODE",
        "simulation",
    ).strip().lower()

    if mode == "simulation":
        _station_backend = StationSimulator()

    elif mode == "real":
        # Only load the real station when it is needed.
        # This avoids connecting to OpenFactory during simulation.
        from liquid_personalization_app.station.openfactory_station import (
            OpenFactoryStation,
        )

        _station_backend = OpenFactoryStation()

    else:
        raise ValueError(
            "STATION_MODE must be either "
            "'simulation' or 'real'."
        )

    return _station_backend
