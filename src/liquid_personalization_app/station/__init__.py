"""Station backend selection for the liquid personalization app."""

from __future__ import annotations

import os

from liquid_personalization_app.station.base import StationBackend
from liquid_personalization_app.station.simulator import StationSimulator


_station_backend: StationBackend | None = None


def get_station_backend() -> StationBackend:
    """Return the configured station backend.

    STATION_MODE=simulation
        Use the local simulator.

    STATION_MODE=real
        Use the physical station through OpenFactory.

    Simulation is the safe default.
    """

    global _station_backend

    if _station_backend is not None:
        return _station_backend

    mode = os.getenv(
        "STATION_MODE",
        "simulation",
    ).strip().lower()

    if mode == "simulation":
        _station_backend = StationSimulator()

    elif mode == "real":
        # Import lazily so local simulation does not try to
        # initialize real OpenFactory infrastructure.
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