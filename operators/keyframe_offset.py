"""Keyframe offset utilities."""

from __future__ import annotations

import bpy
from bpy.props import BoolProperty, EnumProperty, IntProperty
from bpy.types import Context, Operator

from ..properties import AnimationQOLSceneSettings
from ..utils import animation as anim_utils


def _sort_key_by_name(fcurve: bpy.types.FCurve) -> tuple[str, str, str, int]:
    """Produce a deterministic sort key for alphabetical offset mode."""
    group = getattr(fcurve, "group", None)
    group_name = getattr(group, "name", "") if group else ""
    id_data = getattr(fcurve, "id_data", None)
    id_name = getattr(id_data, "name", "") if id_data else ""
    data_path = fcurve.data_path or ""
    return (id_name, group_name, data_path, getattr(fcurve, "array_index", 0))


class ANIMATIONQOL_OT_offset_keyframes(Operator):
    """Shift keyframes uniformly or cascade them by selection/name order."""

    bl_idname = "animation_qol.offset_keyframes"
    bl_label = "Offset Keyframes"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Shift selected keyframes forward or backward in time, with optional cascading by order or name"
    )

    frame_delta: IntProperty(
        name="Frame Offset",
        description="Offset to apply (frames)",
        default=0,
    )
    use_scene_settings: BoolProperty(
        name="Use Scene Settings",
        description="Read the offset configuration from the YABQOLA panel",
        default=True,
        options={"SKIP_SAVE"},
    )
    affect_all_keys: BoolProperty(
        name="Affect All Keys",
        description="Offset all keyframes on the curve, ignoring selection",
        default=False,
    )
    offset_mode: EnumProperty(
        name="Offset Mode",
        description="How to distribute the frame offset across the targeted curves",
        items=(
            ("UNIFORM", "Uniform", "Shift every targeted keyframe by the same amount"),
            ("ORDER", "Selection Order", "Apply an incremental offset following the current curve order"),
            ("NAME", "Name", "Apply an incremental offset sorted alphabetically by curve name"),
        ),
        default="UNIFORM",
    )

    def execute(self, context: Context):
        settings: AnimationQOLSceneSettings | None = getattr(
            context.scene, "animation_qol_settings", None
        )
        if settings is None:
            self.report({"ERROR"}, "YABQOLA settings missing on the scene.")
            return {"CANCELLED"}

        if self.use_scene_settings:
            frame_delta = settings.keyframe_frame_offset
            only_selected = settings.keyframe_only_selected_keys
            mode = settings.keyframe_offset_mode
        else:
            frame_delta = self.frame_delta
            only_selected = not self.affect_all_keys
            mode = self.offset_mode

        if frame_delta == 0:
            self.report({"WARNING"}, "Frame offset is zero; nothing to do.")
            return {"CANCELLED"}

        fcurves = anim_utils.gather_target_fcurves(context, only_selected_curves=True)
        if not fcurves:
            fcurves = anim_utils.gather_target_fcurves(context, only_selected_curves=False)
        if not fcurves:
            self.report({"WARNING"}, "No animation curves available for offset.")
            return {"CANCELLED"}

        ordered_fcurves = list(fcurves)
        if mode == "NAME":
            ordered_fcurves = sorted(ordered_fcurves, key=_sort_key_by_name)

        moved_total = 0
        if mode == "UNIFORM":
            for fcurve in ordered_fcurves:
                moved_total += anim_utils.shift_keyframes(
                    fcurve, frame_delta, only_selected=only_selected
                )
        else:
            for index, fcurve in enumerate(ordered_fcurves):
                curve_delta = frame_delta * index
                if curve_delta == 0:
                    continue
                moved_total += anim_utils.shift_keyframes(
                    fcurve, curve_delta, only_selected=only_selected
                )

        if moved_total == 0:
            self.report(
                {"WARNING"},
                "No keyframes were moved. Select the keys you want to offset or disable 'Only Selected'.",
            )
            return {"CANCELLED"}

        direction = "forward" if frame_delta > 0 else "backward"
        if mode == "UNIFORM":
            self.report(
                {"INFO"},
                f"Offset {moved_total} keyframes {direction} by {abs(frame_delta)} frame(s).",
            )
        else:
            mode_label = "selection order" if mode == "ORDER" else "name order"
            self.report(
                {"INFO"},
                f"Offset {moved_total} keyframes {direction} using a {abs(frame_delta)} frame step ({mode_label}).",
            )
        return {"FINISHED"}


CLASSES = (ANIMATIONQOL_OT_offset_keyframes,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
