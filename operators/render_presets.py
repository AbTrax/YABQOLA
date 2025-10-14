"""Render preset helpers for quick scene setup."""

from __future__ import annotations

import bpy
from bpy.types import Context, Operator

from ..utils.render import apply_render_preset

__all__ = ["ANIMATIONQOL_OT_apply_render_preset"]


class ANIMATIONQOL_OT_apply_render_preset(Operator):
    """Apply the configured render preset to the current scene."""

    bl_idname = "animation_qol.apply_render_preset"
    bl_label = "Apply Render Preset"
    bl_description = "Apply output, sampling, and simplify options for the selected preset"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        scene = context.scene
        settings = getattr(scene, "animation_qol_settings", None)
        if settings is None:
            self.report({"WARNING"}, "Animation QoL settings unavailable on this scene.")
            return {"CANCELLED"}

        preset = settings.render_preset
        adjust_output = settings.render_adjust_output
        adjust_samples = settings.render_adjust_samples

        apply_render_preset(
            scene,
            preset,
            adjust_output=adjust_output,
            adjust_samples=adjust_samples,
        )

        self.report({"INFO"}, f"Applied render preset: {preset.title()}")
        return {"FINISHED"}


CLASSES = (ANIMATIONQOL_OT_apply_render_preset,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
