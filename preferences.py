"""Addon preferences and keymap management for YABQOLA."""

from __future__ import annotations

import bpy
from bpy.props import BoolProperty
from bpy.types import AddonPreferences, Context, KeyMap, KeyMapItem

__all__ = [
    "AnimationQOLPreferences",
    "refresh_keymaps",
    "clear_keymaps",
]

_addon_keymaps: list[tuple[KeyMap, KeyMapItem]] = []


def _get_addon_preferences() -> "AnimationQOLPreferences | None":
    preferences = bpy.context.preferences
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

    if prefs.enable_quick_snap_shortcut:
        km = keyconfigs.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(
            "animation_qol.quick_snap", "F12", "PRESS", ctrl=True, alt=True
        )
        _addon_keymaps.append((km, kmi))

    if prefs.enable_dropper_shortcut:
        km = keyconfigs.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(
            "animation_qol.drop_to_surface", "D", "PRESS", ctrl=True, alt=True
        )
        _addon_keymaps.append((km, kmi))

    if prefs.enable_auto_blink_shortcut:
        km = keyconfigs.keymaps.new(name="Graph Editor", space_type="GRAPH_EDITOR")
        kmi = km.keymap_items.new(
            "animation_qol.generate_auto_blinks", "B", "PRESS", ctrl=True, alt=True
        )
        _addon_keymaps.append((km, kmi))


def refresh_keymaps(context: Context | None = None) -> None:
    context = context or bpy.context
    prefs = _get_addon_preferences()
    if prefs is None:
        return

    _remove_existing_keymaps()
    _install_keymaps(context, prefs)


def _update_keymaps(self, _context: Context) -> None:
    refresh_keymaps()


class AnimationQOLPreferences(AddonPreferences):
    """Addon preferences for shortcut management."""

    bl_idname = __package__

    enable_quick_snap_shortcut: BoolProperty(
        name="Quick Snap Shortcut",
        description="Enable the Ctrl+Alt+F12 shortcut for the Quick Snap operator",
        default=False,
        update=_update_keymaps,
    )
    enable_dropper_shortcut: BoolProperty(
        name="Physics Dropper Shortcut",
        description="Enable the Ctrl+Alt+D shortcut for the Physics Dropper operator",
        default=False,
        update=_update_keymaps,
    )
    enable_auto_blink_shortcut: BoolProperty(
        name="Auto Blink Shortcut",
        description="Enable the Ctrl+Alt+B shortcut for the Auto Blink operator in the Graph Editor",
        default=False,
        update=_update_keymaps,
    )

    def draw(self, _context: Context):
        layout = self.layout
        layout.label(text="Optional Shortcuts", icon="EVENT")
        layout.prop(self, "enable_quick_snap_shortcut")
        layout.prop(self, "enable_dropper_shortcut")
        layout.prop(self, "enable_auto_blink_shortcut")
        layout.label(
            text="Configure or reassign shortcuts via the keymap editor once enabled.",
            icon="INFO",
        )
