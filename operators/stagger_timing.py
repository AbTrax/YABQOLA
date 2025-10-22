"""Timing utilities for staggering animation across multiple objects or bones."""

from __future__ import annotations

from typing import Sequence

import bpy
from bpy.props import BoolProperty, IntProperty
from bpy.types import Context, Object, Operator, PoseBone

from ..properties import AnimationQOLSceneSettings
from ..utils import animation as anim_utils


class ANIMATIONQOL_OT_stagger_keyframes(Operator):
    """Offset animation on selected objects by incremental steps."""

    bl_idname = "animation_qol.stagger_keyframes"
    bl_label = "Stagger Timing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Offsets animation data per object, creating a cascading timing effect. "
        "Uses the scene configuration by default."
    )

    step: IntProperty(
        name="Step",
        description="Frame offset difference between consecutive objects",
        default=3,
    )
    use_scene_settings: BoolProperty(
        name="Use Scene Settings",
        description="Read configuration from the YABQOLA panel",
        default=True,
        options={"SKIP_SAVE"},
    )
    selected_only: BoolProperty(
        name="Selected Keys Only",
        description="When disabled all keyframes on the curves are affected",
        default=True,
    )
    reverse_order: BoolProperty(
        name="Reverse Order",
        description="Apply staggering starting from the last selected object",
        default=False,
    )
    include_shape_keys: BoolProperty(
        name="Shape Keys",
        description="Include shape key animations for the selected objects",
        default=True,
    )

    def execute(self, context: Context):
        settings: AnimationQOLSceneSettings | None = getattr(
            context.scene, "animation_qol_settings", None
        )
        if settings is None:
            self.report({"ERROR"}, "YABQOLA settings missing on the scene.")
            return {"CANCELLED"}

        if self.use_scene_settings:
            step = settings.stagger_step
            selected_only = settings.stagger_selected_only
            reverse_order = settings.stagger_reverse_order
            include_shape_keys = settings.stagger_include_shape_keys
        else:
            step = self.step
            selected_only = self.selected_only
            reverse_order = self.reverse_order
            include_shape_keys = self.include_shape_keys

        if step == 0:
            self.report({"WARNING"}, "Stagger step is zero; adjust the step value to offset timing.")
            return {"CANCELLED"}

        pose_bones = list(getattr(context, "selected_pose_bones", []) or [])
        active_pose_bone = getattr(context, "active_pose_bone", None)
        if active_pose_bone and active_pose_bone not in pose_bones:
            pose_bones.append(active_pose_bone)

        use_bones = len(pose_bones) > 1

        if use_bones and reverse_order:
            pose_bones.reverse()

        if use_bones:
            moved_total = self._stagger_pose_bones(
                pose_bones,
                step=step,
                selected_only=selected_only,
            )
        else:
            objects = list(getattr(context, "selected_objects", []))
            if not objects:
                active_object = getattr(context, "active_object", None)
                if active_object:
                    objects.append(active_object)

            if len(objects) <= 1:
                self.report(
                    {"WARNING"},
                    "Select at least two objects or pose bones to stagger their animation timing.",
                )
                return {"CANCELLED"}

            if reverse_order:
                objects.reverse()

            moved_total = self._stagger_objects(
                objects,
                step=step,
                selected_only=selected_only,
                include_shape_keys=include_shape_keys,
            )

        if moved_total == 0:
            self.report(
                {"WARNING"},
                "No keyframes were staggered. Ensure keys are selected or disable 'Selected Keys Only'.",
            )
            return {"CANCELLED"}

        self.report({"INFO"}, f"Staggered {moved_total} keyframes using a step of {step} frame(s).")
        return {"FINISHED"}

    @staticmethod
    def _stagger_objects(
        objects: Sequence[Object],
        *,
        step: int,
        selected_only: bool,
        include_shape_keys: bool,
    ) -> int:
        moved_total = 0

        for index, obj in enumerate(objects):
            frame_delta = index * step
            if frame_delta == 0:
                continue

            for fcurve in anim_utils.iter_fcurves_for_object(
                obj,
                include_shape_keys=include_shape_keys,
            ):
                if getattr(fcurve, "lock", False):
                    continue
                moved_total += anim_utils.shift_keyframes(
                    fcurve,
                    frame_delta,
                    only_selected=selected_only,
                )

        return moved_total

    @staticmethod
    def _stagger_pose_bones(
        pose_bones: Sequence[PoseBone],
        *,
        step: int,
        selected_only: bool,
    ) -> int:
        moved_total = 0

        for index, pose_bone in enumerate(pose_bones):
            frame_delta = index * step
            if frame_delta == 0:
                continue

            for fcurve in anim_utils.iter_fcurves_for_pose_bone(pose_bone):
                if getattr(fcurve, "lock", False):
                    continue
                moved_total += anim_utils.shift_keyframes(
                    fcurve,
                    frame_delta,
                    only_selected=selected_only,
                )

        return moved_total


CLASSES = (ANIMATIONQOL_OT_stagger_keyframes,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
