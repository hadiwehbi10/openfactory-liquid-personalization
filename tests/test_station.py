"""Tests for station backends."""

from liquid_personalization_app.station.openfactory_station import (
    OpenFactoryStation,
)
from liquid_personalization_app.station.simulator import (
    StationSimulator,
)


class FakeAsset:
    """Small fake OpenFactory Asset used for unit testing."""

    def __init__(self) -> None:
        # Physical sensors are active-low:
        # True = clear
        # False = detected
        self.digital_input_i1 = True
        self.digital_input_i2 = True

        self.relay_2 = False
        self.relay_4 = False


def test_simulator_initial_state():
    station = StationSimulator()

    assert station.get_state() == {
        "sensor1_detected": False,
        "sensor2_detected": False,
        "conveyor_running": False,
        "stopper_engaged": False,
    }


def test_simulator_conveyor_control():
    station = StationSimulator()

    state = station.start_conveyor()

    assert state["conveyor_running"] is True

    state = station.stop_conveyor()

    assert state["conveyor_running"] is False


def test_simulator_stopper_control():
    station = StationSimulator()

    state = station.engage_stopper()

    assert state["stopper_engaged"] is True

    state = station.release_stopper()

    assert state["stopper_engaged"] is False


def test_real_station_normalizes_active_low_sensors():
    asset = FakeAsset()

    station = OpenFactoryStation(
        asset=asset
    )

    # Clear
    asset.digital_input_i1 = True

    assert (
        station.get_state()[
            "sensor1_detected"
        ]
        is False
    )

    # Bottle detected
    asset.digital_input_i1 = False

    assert (
        station.get_state()[
            "sensor1_detected"
        ]
        is True
    )


def test_real_station_controls_conveyor():
    asset = FakeAsset()

    station = OpenFactoryStation(
        asset=asset
    )

    station.start_conveyor()

    assert asset.relay_2 is True

    station.stop_conveyor()

    assert asset.relay_2 is False


def test_real_station_controls_stopper():
    asset = FakeAsset()

    station = OpenFactoryStation(
        asset=asset
    )

    station.engage_stopper()

    assert asset.relay_4 is True

    station.release_stopper()

    assert asset.relay_4 is False