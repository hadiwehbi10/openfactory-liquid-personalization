"""Recipe calculation logic for personalized liquid products."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LiquidRecipe:
    """Computed liquid recipe in milliliters."""

    red_ml: float
    green_ml: float
    blue_ml: float
    base_ml: float
    total_ml: float


def calculate_recipe(red: int, green: int, blue: int, total_volume_ml: float) -> LiquidRecipe:
    """Calculate a simple RGB/base liquid recipe.

    This first version uses the RGB values as relative weights.

    If the selected color is black, meaning RGB(0, 0, 0), the recipe defaults
    to using only base liquid.

    Args:
        red: Red channel value from 0 to 255.
        green: Green channel value from 0 to 255.
        blue: Blue channel value from 0 to 255.
        total_volume_ml: Desired total product volume in milliliters.

    Returns:
        A LiquidRecipe containing the red, green, blue, and base quantities.

    Raises:
        ValueError: If RGB values or total volume are invalid.
    """
    _validate_rgb_value("red", red)
    _validate_rgb_value("green", green)
    _validate_rgb_value("blue", blue)

    if total_volume_ml <= 0:
        raise ValueError("total_volume_ml must be greater than 0")

    color_strength = 0.80
    color_volume_ml = total_volume_ml * color_strength
    base_ml = total_volume_ml - color_volume_ml

    rgb_total = red + green + blue

    if rgb_total == 0:
        return LiquidRecipe(
            red_ml=0.0,
            green_ml=0.0,
            blue_ml=0.0,
            base_ml=round(total_volume_ml, 2),
            total_ml=round(total_volume_ml, 2),
        )

    red_ml = color_volume_ml * red / rgb_total
    green_ml = color_volume_ml * green / rgb_total
    blue_ml = color_volume_ml * blue / rgb_total

    return LiquidRecipe(
        red_ml=round(red_ml, 2),
        green_ml=round(green_ml, 2),
        blue_ml=round(blue_ml, 2),
        base_ml=round(base_ml, 2),
        total_ml=round(red_ml + green_ml + blue_ml + base_ml, 2),
    )


def _validate_rgb_value(name: str, value: int) -> None:
    """Validate one RGB channel value."""
    if not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")

    if value < 0 or value > 255:
        raise ValueError(f"{name} must be between 0 and 255")