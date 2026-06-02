"""OpenFactory Flask app for personalized liquid product orders."""

from __future__ import annotations

import os

from flask import Flask, render_template, request
from openfactory.apps.ofa_flask_app import OpenFactoryFlaskApp
from openfactory.kafka import KSQLDBClient

from liquid_personalization_app.recipe import calculate_recipe


class LiquidPersonalizationApp(OpenFactoryFlaskApp):
    """OpenFactory app with an embedded Flask interface."""

    def create_flask_app(self) -> Flask:
        """Create the Flask app used by the OpenFactory runtime."""
        return Flask(__name__)

    def configure_routes(self) -> None:
        """Configure the web routes for the liquid personalization app."""

        @self.app.get("/")
        def index() -> str:
            return render_template("index.html")

        @self.app.post("/order")
        def create_order() -> str:
            color_hex = request.form["color"]
            volume_ml = float(request.form["volume_ml"])
            label_text = request.form["label_text"]

            red, green, blue = _hex_to_rgb(color_hex)

            recipe = calculate_recipe(
                red=red,
                green=green,
                blue=blue,
                total_volume_ml=volume_ml,
            )

            production_steps = [
                "Create personalized product order",
                "Feed empty bottle into conveyor",
                "Move bottle to filling station",
                "Detect bottle presence",
                "Dispense red, green, blue, and base liquid according to recipe",
                "Move bottle to labeling station",
                "Apply or print custom label",
                "Mark order as complete",
            ]

            return render_template(
                "order_result.html",
                color_hex=color_hex,
                red=red,
                green=green,
                blue=blue,
                volume_ml=volume_ml,
                label_text=label_text,
                recipe=recipe,
                production_steps=production_steps,
            )

        @self.app.get("/health")
        def health() -> dict[str, str]:
            return {"status": "ok"}


def _hex_to_rgb(color_hex: str) -> tuple[int, int, int]:
    """Convert a hex color string to RGB values."""
    normalized = color_hex.lstrip("#")

    if len(normalized) != 6:
        raise ValueError("color_hex must contain 6 hexadecimal characters")

    red = int(normalized[0:2], 16)
    green = int(normalized[2:4], 16)
    blue = int(normalized[4:6], 16)

    return red, green, blue


def create_app(test_mode: bool = True) -> LiquidPersonalizationApp:
    """Create the OpenFactory Flask app.

    The default test_mode=True lets the app run locally without requiring
    a full OpenFactory/Kafka environment.
    """
    return LiquidPersonalizationApp(
        ksqlClient=KSQLDBClient(os.getenv("KSQLDB_URL", "http://localhost:8088")),
        bootstrap_servers=os.getenv("KAFKA_BROKER", "localhost:9092"),
        asset_router_url=os.getenv("ASSET_ROUTER_URL"),
        loglevel=os.getenv("LOG_LEVEL", "INFO"),
        test_mode=test_mode,
    )


def main() -> None:
    """Run the OpenFactory Flask application."""
    test_mode = os.getenv("OPENFACTORY_TEST_MODE", "false").lower() == "true"
    app = create_app(test_mode=test_mode)
    app.run()


if __name__ == "__main__":
    main()