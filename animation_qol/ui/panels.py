"""UI panels for Animation QoL."""

from __future__ import annotations

import bpy
from bpy.types import Context, Panel

from ..properties import AnimationQOLSceneSettings


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


class ANIMATIONQOL_PT_base(Panel):
    bl_label = "Animation QoL"
    bl_region_type = "UI"
    bl_category = "Anim QOL"

    @classmethod
    def poll(cls, context: Context) -> bool:
        return getattr(context.scene, "animation_qol_settings", None) is not None

    def draw(self, context: Context):
        layout = self.layout
        settings: AnimationQOLSceneSettings | None = getattr(
            context.scene, "animation_qol_settings", None
        )

        if settings is None:
            layout.label(text="Scene settings unavailable", icon="ERROR")
            return

        _draw_noise_section(layout.box(), settings)
        layout.separator()
        _draw_offset_section(layout.box(), settings)
        layout.separator()
        _draw_stagger_section(layout.box(), settings)


class ANIMATIONQOL_PT_graph_editor(ANIMATIONQOL_PT_base):
    bl_space_type = "GRAPH_EDITOR"


class ANIMATIONQOL_PT_dopesheet(ANIMATIONQOL_PT_base):
    bl_space_type = "DOPESHEET_EDITOR"


CLASSES = (
    ANIMATIONQOL_PT_graph_editor,
    ANIMATIONQOL_PT_dopesheet,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)