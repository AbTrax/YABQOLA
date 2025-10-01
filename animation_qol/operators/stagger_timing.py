"""Timing utilities for staggering animation across multiple objects."""

from __future__ import annotations

import bpy
from bpy.props import BoolProperty, IntProperty
from bpy.types import Context, Operator

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
        description="Read configuration from the Animation QoL panel",
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
            self.report({"ERROR"}, "Animation QoL settings missing on the scene.")
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

        objects = list(getattr(context, "selected_objects", []))
        if not objects:
            active = getattr(context, "active_object", None)
            if active:
                objects.append(active)

        if len(objects) <= 1:
            self.report({"WARNING"}, "Select at least two objects to stagger their animation timing.")
            return {"CANCELLED"}

        if reverse_order:
            objects.reverse()

        moved_total = 0

        for index, obj in enumerate(objects):
            frame_delta = index * step
            if frame_delta == 0:
                continue

            for fcurve in anim_utils.iter_fcurves_for_object(
                obj, include_shape_keys=include_shape_keys
            ):
                if getattr(fcurve, "lock", False):
                    continue
                moved_total += anim_utils.shift_keyframes(
                    fcurve,
                    frame_delta,
                    only_selected=selected_only,
                )

        if moved_total == 0:
            self.report(
                {"WARNING"},
                "No keyframes were staggered. Ensure keys are selected or disable 'Selected Keys Only'.",
            )
            return {"CANCELLED"}

        self.report({"INFO"}, f"Staggered {moved_total} keyframes using a step of {step} frame(s).")
        return {"FINISHED"}


CLASSES = (ANIMATIONQOL_OT_stagger_keyframes,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)