"""Addon preferences and keymap management for YABQOLA."""

from __future__ import annotations

import bpy
from bpy.props import BoolProperty
from bpy.types import AddonPreferences, Context, KeyMap, KeyMapItem

__all__ = [
    "AnimationQOLPreferences",
    "get_addon_preferences",
    "refresh_keymaps",
    "clear_keymaps",
    "register",
    "unregister",
]

_addon_keymaps: list[tuple[KeyMap, KeyMapItem]] = []


def get_addon_preferences(context: Context | None = None) -> "AnimationQOLPreferences | None":
    context = context or bpy.context
    if context is None:
        return None

    preferences = context.preferences
    addon = preferences.addons.get(__package__)
    if addon is None:
        return None
    return addon.preferences


def _remove_existing_keymaps() -> None:
    while _addon_keymaps:
        km, kmi = _addon_keymaps.pop()
        km.keymap_items.remove(kmi)


def clear_keymaps() -> None:
    _remove_existing_keymaps()


def _install_keymaps(context: Context, prefs: "AnimationQOLPreferences") -> None:
    window_manager = context.window_manager
    if window_manager is None:
        return

    keyconfigs = window_manager.keyconfigs.addon
    if keyconfigs is None:
        return

    # No optional keymaps currently installed.


def refresh_keymaps(context: Context | None = None) -> None:
    context = context or bpy.context
    prefs = get_addon_preferences(context)
    if prefs is None:
        return

    _remove_existing_keymaps()
    _install_keymaps(context, prefs)


def _update_keymaps(self, _context: Context) -> None:
    refresh_keymaps()


class AnimationQOLPreferences(AddonPreferences):
    """Addon preferences for shortcut management."""

    bl_idname = __package__

    enable_noise_randomizer_tools: BoolProperty(
        name="Noise Randomizer",
        description="Show the Noise Randomizer tools",
        default=True,
    )
    enable_keyframe_offset_tools: BoolProperty(
        name="Keyframe Offset",
        description="Show the Keyframe Offset tools",
        default=True,
    )
    enable_stagger_timing_tools: BoolProperty(
        name="Stagger Timing",
        description="Show the Stagger Timing tools",
        default=True,
    )
    enable_ease_presets_tools: BoolProperty(
        name="Ease Presets",
        description="Show the Ease Presets tools",
        default=True,
    )
    enable_motion_hold_tools: BoolProperty(
        name="Motion Hold",
        description="Show the Motion Hold tools",
        default=True,
    )
    enable_quick_flip_tools: BoolProperty(
        name="Quick Flip",
        description="Show the Quick Flip tools",
        default=True,
    )
    enable_scene_cleanup_tools: BoolProperty(
        name="Scene Cleanup",
        description="Show the Scene Cleanup tools",
        default=True,
    )
    enable_render_presets_tools: BoolProperty(
        name="Render Presets",
        description="Show the Render Presets tools",
        default=True,
    )
    def draw(self, _context: Context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        feature_box = layout.box()
        feature_box.label(text="Feature Visibility", icon="PREFERENCES")
        column = feature_box.column(align=True)
        column.prop(self, "enable_noise_randomizer_tools")
        column.prop(self, "enable_keyframe_offset_tools")
        column.prop(self, "enable_stagger_timing_tools")
        column.prop(self, "enable_ease_presets_tools")
        column.prop(self, "enable_motion_hold_tools")
        column.prop(self, "enable_quick_flip_tools")
        column.prop(self, "enable_scene_cleanup_tools")
        column.prop(self, "enable_render_presets_tools")


def register() -> None:
    bpy.utils.register_class(AnimationQOLPreferences)
    refresh_keymaps()


def unregister() -> None:
    clear_keymaps()
    bpy.utils.unregister_class(AnimationQOLPreferences)
