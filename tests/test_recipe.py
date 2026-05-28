"""Tests for recipe calculation logic."""

import pytest

from liquid_personalization_app.recipe import LiquidRecipe, calculate_recipe


def test_calculate_recipe_for_red_color() -> None:
    recipe = calculate_recipe(red=255, green=0, blue=0, total_volume_ml=250)

    assert recipe == LiquidRecipe(
        red_ml=200.0,
        green_ml=0.0,
        blue_ml=0.0,
        base_ml=50.0,
        total_ml=250.0,
    )


def test_calculate_recipe_for_balanced_white_color() -> None:
    recipe = calculate_recipe(red=255, green=255, blue=255, total_volume_ml=300)

    assert recipe.red_ml == 80.0
    assert recipe.green_ml == 80.0
    assert recipe.blue_ml == 80.0
    assert recipe.base_ml == 60.0
    assert recipe.total_ml == 300.0


def test_calculate_recipe_for_black_color_uses_only_base() -> None:
    recipe = calculate_recipe(red=0, green=0, blue=0, total_volume_ml=250)

    assert recipe.red_ml == 0.0
    assert recipe.green_ml == 0.0
    assert recipe.blue_ml == 0.0
    assert recipe.base_ml == 250.0
    assert recipe.total_ml == 250.0


def test_calculate_recipe_rejects_invalid_rgb_value() -> None:
    with pytest.raises(ValueError, match="red must be between 0 and 255"):
        calculate_recipe(red=300, green=0, blue=0, total_volume_ml=250)


def test_calculate_recipe_rejects_invalid_volume() -> None:
    with pytest.raises(ValueError, match="total_volume_ml must be greater than 0"):
        calculate_recipe(red=10, green=20, blue=30, total_volume_ml=0)