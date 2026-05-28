"""Flask-based OpenFactory app for personalized liquid product orders."""

from __future__ import annotations

from flask import Flask, render_template, request

from liquid_personalization_app.recipe import calculate_recipe


def create_flask_app() -> Flask:
    """Create and configure the Flask web application."""
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.post("/order")
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

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def _hex_to_rgb(color_hex: str) -> tuple[int, int, int]:
    """Convert a hex color string to RGB values."""
    normalized = color_hex.lstrip("#")

    if len(normalized) != 6:
        raise ValueError("color_hex must contain 6 hexadecimal characters")

    red = int(normalized[0:2], 16)
    green = int(normalized[2:4], 16)
    blue = int(normalized[4:6], 16)

    return red, green, blue


def main() -> None:
    """Run the Flask application locally."""
    app = create_flask_app()
    app.run(host="0.0.0.0", port=4000, debug=True)


if __name__ == "__main__":
    main()