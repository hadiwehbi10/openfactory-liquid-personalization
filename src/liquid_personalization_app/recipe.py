
"""Calculate liquid quantities for personalized RGB products.

The user chooses an RGB color and a total liquid volume.
This module calculates how much red, green, blue, and base
liquid should be used.

The current formula is a simple starting model, not a
calibrated method for producing exact physical colors.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LiquidRecipe:
    """Store the calculated liquid quantities in milliliters.

    Each value represents the amount of one liquid needed.
    The recipe cannot be modified after it is created.
    """

    red_ml: float
    green_ml: float
    blue_ml: float
    base_ml: float
    total_ml: float


def calculate_recipe(
    red: int,
    green: int,
    blue: int,
    total_volume_ml: float,
) -> LiquidRecipe:
    """Calculate a liquid recipe from an RGB color and total volume.

    The current model assigns 80% of the total volume to
    RGB liquids and 20% to base liquid.

    The RGB values determine the relative amounts of each color.
    For RGB(0, 0, 0), the recipe uses only base liquid.

    Args:
        red: Red channel value (0-255).
        green: Green channel value (0-255).
        blue: Blue channel value (0-255).
        total_volume_ml: Requested liquid volume in milliliters.

    Returns:
        A recipe containing the calculated liquid quantities.

    Raises:
        ValueError: If an RGB value or the volume is invalid.
    """
    _validate_rgb_value("red", red)
    _validate_rgb_value("green", green)
    _validate_rgb_value("blue", blue)

    if total_volume_ml <= 0:
        raise ValueError("total_volume_ml must be greater than 0")

    # Initial mixing assumption: 80% color liquids, 20% base.
    color_strength = 0.80
    color_volume_ml = total_volume_ml * color_strength
    base_ml = total_volume_ml - color_volume_ml

    rgb_total = red + green + blue

    # Black is treated as a base-only recipe in this model.
    if rgb_total == 0:
        return LiquidRecipe(
            red_ml=0.0,
            green_ml=0.0,
            blue_ml=0.0,
            base_ml=round(total_volume_ml, 2),
            total_ml=round(total_volume_ml, 2),
        )

    # Divide the color volume according to the RGB proportions.
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
    """Check that an RGB channel is an integer between 0 and 255."""
    if not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")

    if value < 0 or value > 255:
        raise ValueError(f"{name} must be between 0 and 255")
