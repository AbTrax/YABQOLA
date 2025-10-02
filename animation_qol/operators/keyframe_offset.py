"""Keyframe offset utilities."""

from __future__ import annotations

import bpy
from bpy.props import BoolProperty, IntProperty
from bpy.types import Context, Operator

from ..properties import AnimationQOLSceneSettings
from ..utils import animation as anim_utils


class ANIMATIONQOL_OT_offset_keyframes(Operator):
    """Shift selected keyframe points by a fixed number of frames."""

    bl_idname = "animation_qol.offset_keyframes"
    bl_label = "Offset Keyframes"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Shift selected keyframes forward or backward by a fixed amount"

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
        else:
            frame_delta = self.frame_delta
            only_selected = not self.affect_all_keys

        if frame_delta == 0:
            self.report({"WARNING"}, "Frame offset is zero; nothing to do.")
            return {"CANCELLED"}

        fcurves = anim_utils.gather_target_fcurves(context, only_selected_curves=True)
        if not fcurves:
            fcurves = anim_utils.gather_target_fcurves(context, only_selected_curves=False)
        if not fcurves:
            self.report({"WARNING"}, "No animation curves available for offset.")
            return {"CANCELLED"}

        moved_total = 0
        for fcurve in fcurves:
            moved_total += anim_utils.shift_keyframes(fcurve, frame_delta, only_selected=only_selected)

        if moved_total == 0:
            self.report(
                {"WARNING"},
                "No keyframes were moved. Select the keys you want to offset or disable 'Only Selected'.",
            )
            return {"CANCELLED"}

        direction = "forward" if frame_delta > 0 else "backward"
        self.report(
            {"INFO"},
            f"Offset {moved_total} keyframes {direction} by {abs(frame_delta)} frame(s).",
        )
        return {"FINISHED"}


CLASSES = (ANIMATIONQOL_OT_offset_keyframes,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)