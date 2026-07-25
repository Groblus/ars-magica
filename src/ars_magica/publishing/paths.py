"""Locations for publishing resources bundled in the installed package."""

from importlib.resources import files


PRESS_ROOT = files("ars_magica.publishing.resources").joinpath("press")
TEMPLATE_ROOT = PRESS_ROOT / "templates"
TOKEN_ROOT = PRESS_ROOT / "tokens"
THEME_ROOT = PRESS_ROOT / "themes"
PRESET_ROOT = PRESS_ROOT / "presets"
STYLE_ROOT = PRESS_ROOT / "styles"
