"""UI panels for YABQOLA (Yet Another Blender QoL Add-on)."""

from __future__ import annotations

import bpy
from bpy.types import Context, Panel

from ..preferences import get_addon_preferences
from ..properties import AnimationQOLSceneSettings


def _get_settings(context: Context) -> AnimationQOLSceneSettings | None:
    return getattr(context.scene, "animation_qol_settings", None)


def _feature_enabled(prefs, attr: str) -> bool:
    if prefs is None:
        return True
    return getattr(prefs, attr, True)


def _any_features_enabled(prefs, *attrs: str) -> bool:
    return any(_feature_enabled(prefs, attr) for attr in attrs)


def _draw_noise_section(layout, settings: AnimationQOLSceneSettings):
    layout.label(text="Noise Randomizer", icon="RNDCURVE")
    col = layout.column(align=True)
    col.prop(settings, "noise_seed")
    row = col.row(align=True)
    row.prop(settings, "noise_phase_min")
    row.prop(settings, "noise_phase_max")
    row = col.row(align=True)
    row.prop(settings, "noise_offset_min")
    row.prop(settings, "noise_offset_max")
    row = col.row(align=True)
    row.prop(settings, "noise_strength_min")
    row.prop(settings, "noise_strength_max")
    row = col.row(align=True)
    row.prop(settings, "noise_scale_min")
    row.prop(settings, "noise_scale_max")
    col.prop(settings, "noise_create_missing")
    col.operator(
        "animation_qol.randomize_noise_modifiers",
        icon="RNDCURVE",
        text="Randomize Noise",
    )


def _draw_offset_section(layout, settings: AnimationQOLSceneSettings):
    layout.label(text="Keyframe Offset", icon="TIME")
    col = layout.column(align=True)
    col.prop(settings, "keyframe_frame_offset")
    col.prop(settings, "keyframe_only_selected_keys")
    col.prop(settings, "keyframe_offset_mode")
    col.operator(
        "animation_qol.offset_keyframes",
        icon="FRAME_NEXT",
        text="Apply Offset",
    )


def _draw_stagger_section(layout, settings: AnimationQOLSceneSettings):
    layout.label(text="Stagger Timing", icon="SEQ_CHROMA_SCOPE")
    col = layout.column(align=True)
    col.prop(settings, "stagger_step")
    col.prop(settings, "stagger_selected_only")
    col.prop(settings, "stagger_reverse_order")
    col.prop(settings, "stagger_include_shape_keys")
    col.operator(
        "animation_qol.stagger_keyframes",
        icon="SEQ_LUMA_WAVEFORM",
        text="Stagger",
    )


def _draw_ease_section(layout, settings: AnimationQOLSceneSettings):
    layout.label(text="Ease Presets", icon="IPO_BEZIER")
    col = layout.column(align=True)
    col.prop(settings, "ease_preset")
    col.prop(settings, "ease_only_selected_curves")
    col.prop(settings, "ease_only_selected_keys")
    col.prop(settings, "ease_include_shape_keys")
    col.prop(settings, "ease_affect_handles")
    col.operator(
        "animation_qol.apply_ease_preset",
        icon="HANDLE_AUTO",
        text="Apply Ease",
    )


def _draw_hold_section(layout, settings: AnimationQOLSceneSettings):
    layout.label(text="Motion Hold", icon="PAUSE")
    col = layout.column(align=True)
    col.prop(settings, "hold_frame_count")
    col.prop(settings, "hold_interpolation")
    col.prop(settings, "hold_only_selected_curves")
    col.prop(settings, "hold_only_selected_keys")
    col.prop(settings, "hold_include_shape_keys")
    col.prop(settings, "hold_inherit_handles")
    col.operator(
        "animation_qol.insert_motion_hold",
        icon="KEY_HLT",
        text="Insert Hold",
    )


def _draw_blink_section(layout, settings: AnimationQOLSceneSettings):
    layout.label(text="Auto Blink", icon="HIDE_OFF")
    col = layout.column(align=True)
    col.prop(settings, "blink_shape_key_name")
    col.prop(settings, "blink_strength", slider=True)
    col.prop(settings, "blink_use_selected_objects")
    row = col.row(align=True)
    row.prop(settings, "blink_frame_start")
    row.prop(settings, "blink_frame_end")
    row = col.row(align=True)
    row.prop(settings, "blink_interval")
    row.prop(settings, "blink_interval_random")
    row = col.row(align=True)
    row.prop(settings, "blink_close_frames")
    row.prop(settings, "blink_open_frames")
    col.prop(settings, "blink_hold_frames")
    col.prop(settings, "blink_seed")
    col.operator(
        "animation_qol.generate_auto_blinks",
        icon="HIDE_OFF",
        text="Generate Blinks",
    )


def _draw_quick_flip_section(layout, settings: AnimationQOLSceneSettings):
    layout.label(text="Quick Flip", icon="ARROW_LEFTRIGHT")
    col = layout.column(align=True)
    col.prop(settings, "flip_scope", expand=True)
    if settings.flip_scope == "COLLECTION":
        col.prop(settings, "flip_collection")
        col.prop(settings, "flip_include_subcollections")
    col.prop(settings, "flip_include_children")
    col.separator()
    col.prop(settings, "flip_axis", expand=True)
    col.separator()
    col.operator("animation_qol.flip_smart", icon="ARROW_LEFTRIGHT", text="Smart Flip")
    row = col.row(align=True)
    row.operator("animation_qol.flip_pose_only", icon="ARMATURE_DATA", text="Flip Pose")
    row.operator("animation_qol.flip_objects_only", icon="EMPTY_ARROWS", text="Flip Objects")


def _draw_cleanup_section(layout, settings: AnimationQOLSceneSettings):
    layout.label(text="Scene Cleanup", icon="TRASH")
    col = layout.column(align=True)
    col.prop(settings, "cleanup_consider_viewport")
    col.prop(settings, "cleanup_consider_render")
    col.separator()
    col.prop(settings, "cleanup_keep_lights")
    row = col.row(align=True)
    row.prop(settings, "cleanup_keep_cameras")
    row.prop(settings, "cleanup_keep_active_camera")
    col.prop(settings, "cleanup_exclude_linked_data")
    col.separator()
    row = col.row(align=True)
    preview_op = row.operator(
        "animation_qol.cleanup_invisible",
        icon="HIDE_OFF",
        text="Preview",
    )
    preview_op.dry_run = True
    delete_op = row.operator(
        "animation_qol.cleanup_invisible",
        icon="TRASH",
        text="Delete",
    )
    delete_op.dry_run = False


def _draw_render_section(layout, settings: AnimationQOLSceneSettings):
    layout.label(text="Render Presets", icon="RENDER_STILL")
    col = layout.column(align=True)
    col.prop(settings, "render_preset")
    col.prop(settings, "render_adjust_output")
    col.prop(settings, "render_adjust_samples")
    col.operator(
        "animation_qol.apply_render_preset",
        icon="RENDER_ANIMATION",
        text="Apply Render Preset",
    )


class ANIMATIONQOL_PT_base(Panel):
    bl_label = "YABQOLA"
    bl_region_type = "UI"
    bl_category = "YABQOLA"

    @classmethod
    def poll(cls, context: Context) -> bool:
        return _get_settings(context) is not None

    def draw(self, context: Context):
        layout = self.layout
        settings = _get_settings(context)
        prefs = get_addon_preferences(context)

        if settings is None:
            layout.label(text="Scene settings unavailable", icon="ERROR")
            return

        sections = [
            ("enable_noise_randomizer_tools", _draw_noise_section),
            ("enable_keyframe_offset_tools", _draw_offset_section),
            ("enable_stagger_timing_tools", _draw_stagger_section),
            ("enable_ease_presets_tools", _draw_ease_section),
            ("enable_motion_hold_tools", _draw_hold_section),
            ("enable_auto_blink_tools", _draw_blink_section),
        ]

        first_section_drawn = False
        for attr, drawer in sections:
            if not _feature_enabled(prefs, attr):
                continue
            if first_section_drawn:
                layout.separator()
            drawer(layout.box(), settings)
            first_section_drawn = True

        if not first_section_drawn:
            layout.label(
                text="All features hidden via add-on preferences.",
                icon="INFO",
            )


class ANIMATIONQOL_PT_graph_editor(ANIMATIONQOL_PT_base):
    bl_space_type = "GRAPH_EDITOR"
    bl_options = {"DEFAULT_CLOSED"}


class ANIMATIONQOL_PT_dopesheet(ANIMATIONQOL_PT_base):
    bl_space_type = "DOPESHEET_EDITOR"
    bl_options = {"DEFAULT_CLOSED"}


class ANIMATIONQOL_PT_view3d_quick_flip(Panel):
    bl_label = "YABQOLA: Quick Flip"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "YABQOLA"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        if _get_settings(context) is None:
            return False
        prefs = get_addon_preferences(context)
        return _feature_enabled(prefs, "enable_quick_flip_tools")

    def draw(self, context: Context):
        layout = self.layout
        settings = _get_settings(context)
        prefs = get_addon_preferences(context)

        if settings is None:
            layout.label(text="Scene settings unavailable", icon="ERROR")
            return

        if _feature_enabled(prefs, "enable_quick_flip_tools"):
            _draw_quick_flip_section(layout.box(), settings)
        else:
            layout.label(text="Quick Flip tools disabled in preferences.", icon="INFO")


class ANIMATIONQOL_PT_view3d_cleanup(Panel):
    bl_label = "YABQOLA: Scene Cleanup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "YABQOLA"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        if _get_settings(context) is None:
            return False
        prefs = get_addon_preferences(context)
        return _feature_enabled(prefs, "enable_scene_cleanup_tools")

    def draw(self, context: Context):
        layout = self.layout
        settings = _get_settings(context)
        prefs = get_addon_preferences(context)

        if settings is None:
            layout.label(text="Scene settings unavailable", icon="ERROR")
            return

        if _feature_enabled(prefs, "enable_scene_cleanup_tools"):
            _draw_cleanup_section(layout.box(), settings)
        else:
            layout.label(text="Scene Cleanup tools disabled in preferences.", icon="INFO")


class ANIMATIONQOL_PT_view3d_render(Panel):
    bl_label = "YABQOLA: Render Presets"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "YABQOLA"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        if _get_settings(context) is None:
            return False
        prefs = get_addon_preferences(context)
        return _feature_enabled(prefs, "enable_render_presets_tools")

    def draw(self, context: Context):
        layout = self.layout
        settings = _get_settings(context)
        prefs = get_addon_preferences(context)

        if settings is None:
            layout.label(text="Scene settings unavailable", icon="ERROR")
            return

        if _feature_enabled(prefs, "enable_render_presets_tools"):
            _draw_render_section(layout.box(), settings)
        else:
            layout.label(text="Render tools disabled in preferences.", icon="INFO")


CLASSES = (
    ANIMATIONQOL_PT_graph_editor,
    ANIMATIONQOL_PT_dopesheet,
    ANIMATIONQOL_PT_view3d_quick_flip,
    ANIMATIONQOL_PT_view3d_cleanup,
    ANIMATIONQOL_PT_view3d_render,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
