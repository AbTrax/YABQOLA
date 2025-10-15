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

    if prefs.enable_quick_snap_tools and prefs.enable_quick_snap_shortcut:
        km = keyconfigs.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(
            "animation_qol.quick_snap", "F12", "PRESS", ctrl=True, alt=True
        )
        _addon_keymaps.append((km, kmi))

    if prefs.enable_physics_dropper_tools and prefs.enable_dropper_shortcut:
        km = keyconfigs.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(
            "animation_qol.drop_to_surface", "D", "PRESS", ctrl=True, alt=True
        )
        _addon_keymaps.append((km, kmi))

    if prefs.enable_auto_blink_tools and prefs.enable_auto_blink_shortcut:
        km = keyconfigs.keymaps.new(name="Graph Editor", space_type="GRAPH_EDITOR")
        kmi = km.keymap_items.new(
            "animation_qol.generate_auto_blinks", "B", "PRESS", ctrl=True, alt=True
        )
        _addon_keymaps.append((km, kmi))


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
    enable_auto_blink_tools: BoolProperty(
        name="Auto Blink",
        description="Show the Auto Blink tools",
        default=True,
    )
    enable_quick_flip_tools: BoolProperty(
        name="Quick Flip",
        description="Show the Quick Flip tools",
        default=True,
    )
    enable_physics_dropper_tools: BoolProperty(
        name="Physics Dropper",
        description="Show the Physics Dropper tools",
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
    enable_quick_snap_tools: BoolProperty(
        name="Quick Snap",
        description="Show the Quick Snap tools",
        default=True,
    )

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
        column.prop(self, "enable_auto_blink_tools")
        column.prop(self, "enable_quick_flip_tools")
        column.prop(self, "enable_physics_dropper_tools")
        column.prop(self, "enable_scene_cleanup_tools")
        column.prop(self, "enable_render_presets_tools")
        column.prop(self, "enable_quick_snap_tools")

        shortcuts_box = layout.box()
        shortcuts_box.label(text="Optional Shortcuts", icon="KEYFRAME")
        row = shortcuts_box.row()
        row.enabled = self.enable_quick_snap_tools
        row.prop(self, "enable_quick_snap_shortcut")
        row = shortcuts_box.row()
        row.enabled = self.enable_physics_dropper_tools
        row.prop(self, "enable_dropper_shortcut")
        row = shortcuts_box.row()
        row.enabled = self.enable_auto_blink_tools
        row.prop(self, "enable_auto_blink_shortcut")
        shortcuts_box.label(
            text="Configure or reassign shortcuts via the keymap editor once enabled.",
            icon="INFO",
        )


def register() -> None:
    bpy.utils.register_class(AnimationQOLPreferences)
    refresh_keymaps()


def unregister() -> None:
    clear_keymaps()
    bpy.utils.unregister_class(AnimationQOLPreferences)
