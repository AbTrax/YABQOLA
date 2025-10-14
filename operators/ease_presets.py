"""Ease preset utilities for animators."""

from __future__ import annotations

from typing import Iterable

import bpy
from bpy.types import Context, Keyframe, Operator

from ..utils.animation import gather_target_fcurves

__all__ = ["ANIMATIONQOL_OT_apply_ease_preset"]


def _iter_target_keyframes(
    fcurve,
    *,
    only_selected_keys: bool,
) -> Iterable[Keyframe]:
    for point in fcurve.keyframe_points:
        if only_selected_keys and not point.select_control_point:
            continue
        yield point


def _apply_preset_to_keyframe(keyframe: Keyframe, preset: str, affect_handles: bool) -> None:
    """Set easing controls for ``keyframe`` according to ``preset``."""

    if preset == "LINEAR":
        keyframe.interpolation = "LINEAR"
        if affect_handles:
            keyframe.handle_left_type = "VECTOR"
            keyframe.handle_right_type = "VECTOR"
        return

    if preset == "CONSTANT":
        keyframe.interpolation = "CONSTANT"
        return

    keyframe.interpolation = "BEZIER"

    if not affect_handles:
        return

    if preset == "EASE_IN":
        keyframe.handle_left_type = "AUTO_CLAMPED"
        keyframe.handle_right_type = "VECTOR"
    elif preset == "EASE_OUT":
        keyframe.handle_left_type = "VECTOR"
        keyframe.handle_right_type = "AUTO_CLAMPED"
    else:  # EASE_IN_OUT
        keyframe.handle_left_type = "AUTO_CLAMPED"
        keyframe.handle_right_type = "AUTO_CLAMPED"


class ANIMATIONQOL_OT_apply_ease_preset(Operator):
    """Apply the configured ease preset to targeted keyframes."""

    bl_idname = "animation_qol.apply_ease_preset"
    bl_label = "Apply Ease Preset"
    bl_description = "Apply handle and interpolation presets to the targeted keyframes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        scene = context.scene
        settings = getattr(scene, "animation_qol_settings", None)
        if settings is None:
            self.report({"WARNING"}, "Animation QoL settings unavailable on this scene.")
            return {"CANCELLED"}

        preset = settings.ease_preset
        only_selected_curves = settings.ease_only_selected_curves
        include_shape_keys = settings.ease_include_shape_keys
        only_selected_keys = settings.ease_only_selected_keys
        affect_handles = settings.ease_affect_handles

        fcurves = gather_target_fcurves(
            context,
            only_selected_curves=only_selected_curves,
            include_shape_keys=include_shape_keys,
        )

        if not fcurves:
            self.report({"INFO"}, "No editable F-Curves detected for the operation.")
            return {"CANCELLED"}

        edited = 0

        for fcurve in fcurves:
            changed = False
            for keyframe in _iter_target_keyframes(
                fcurve,
                only_selected_keys=only_selected_keys,
            ):
                _apply_preset_to_keyframe(keyframe, preset, affect_handles)
                changed = True

            if changed:
                fcurve.update()
                edited += 1

        if not edited:
            self.report({"INFO"}, "No keyframes met the selection criteria.")
            return {"CANCELLED"}

        return {"FINISHED"}


CLASSES = (ANIMATIONQOL_OT_apply_ease_preset,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
