"""Motion hold utilities for animators."""

from __future__ import annotations

from typing import Iterable

import bpy
from bpy.types import Context, Keyframe, Operator

from ..utils.animation import gather_target_fcurves

__all__ = ["ANIMATIONQOL_OT_insert_motion_hold"]


def _iter_source_keyframes(
    fcurve,
    *,
    only_selected_keys: bool,
) -> Iterable[Keyframe]:
    if only_selected_keys:
        return (kp for kp in fcurve.keyframe_points if kp.select_control_point)
    return iter(fcurve.keyframe_points)


def _keyframe_exists(fcurve, frame: float) -> bool:
    epsilon = 1e-4
    return any(abs(kp.co.x - frame) <= epsilon for kp in fcurve.keyframe_points)


def _duplicate_keyframe(
    fcurve,
    source: Keyframe,
    *,
    frame_delta: float,
    interpolation: str,
    inherit_handles: bool,
) -> None:
    new_frame = source.co.x + frame_delta
    if _keyframe_exists(fcurve, new_frame):
        return

    new_key = fcurve.keyframe_points.insert(
        frame=new_frame,
        value=source.co.y,
        options={"FAST"},
    )
    new_key.interpolation = interpolation
    new_key.select_control_point = True

    if inherit_handles and source.interpolation == "BEZIER":
        dx = source.handle_right.x - source.co.x
        dy = source.handle_right.y - source.co.y
        new_key.handle_left = (new_key.co.x - dx, new_key.co.y - dy)
        new_key.handle_right = (new_key.co.x + 1e-3, new_key.co.y)
        new_key.handle_left_type = source.handle_right_type
        new_key.handle_right_type = "AUTO_CLAMPED"
    elif interpolation == "CONSTANT":
        new_key.handle_left_type = "FREE"
        new_key.handle_right_type = "FREE"
        new_key.handle_left = (new_key.co.x - 0.1, new_key.co.y)
        new_key.handle_right = (new_key.co.x + 0.1, new_key.co.y)
    else:
        new_key.handle_left_type = "AUTO_CLAMPED"
        new_key.handle_right_type = "AUTO_CLAMPED"


class ANIMATIONQOL_OT_insert_motion_hold(Operator):
    """Duplicate keyframes forward in time to create a motion hold."""

    bl_idname = "animation_qol.insert_motion_hold"
    bl_label = "Insert Motion Hold"
    bl_description = "Duplicate the selected keyframes forward in time to create a hold"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        scene = context.scene
        settings = getattr(scene, "animation_qol_settings", None)
        if settings is None:
            self.report({"WARNING"}, "Animation QoL settings unavailable on this scene.")
            return {"CANCELLED"}

        frame_offset = max(1, settings.hold_frame_count)
        only_selected_curves = settings.hold_only_selected_curves
        include_shape_keys = settings.hold_include_shape_keys
        only_selected_keys = settings.hold_only_selected_keys
        interpolation = settings.hold_interpolation
        inherit_handles = settings.hold_inherit_handles

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
            for keyframe in _iter_source_keyframes(
                fcurve,
                only_selected_keys=only_selected_keys,
            ):
                _duplicate_keyframe(
                    fcurve,
                    keyframe,
                    frame_delta=frame_offset,
                    interpolation=interpolation,
                    inherit_handles=inherit_handles,
                )
                if interpolation == "CONSTANT":
                    keyframe.interpolation = "CONSTANT"
                changed = True

            if changed:
                fcurve.update()
                edited += 1

        if not edited:
            self.report({"INFO"}, "No keyframes met the selection criteria.")
            return {"CANCELLED"}

        return {"FINISHED"}


CLASSES = (ANIMATIONQOL_OT_insert_motion_hold,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
