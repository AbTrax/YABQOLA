"""Quick flip operators for mirroring poses and objects."""

from __future__ import annotations

import bpy
from bpy.types import Context, Operator

from ..properties import AnimationQOLSceneSettings
from ..utils import objects as obj_utils


_AXIS_TO_INDEX = {"X": 0, "Y": 1, "Z": 2}


def _gather_targets(context: Context, settings: AnimationQOLSceneSettings):
    return obj_utils.gather_scope_objects(
        context,
        settings.flip_include_children,
        scope=settings.flip_scope,
        collection=settings.flip_collection,
        include_subcollections=settings.flip_include_subcollections,
    )


class ANIMATIONQOL_OT_flip_smart(Operator):
    """Flip poses for armatures and mirror other objects using a shared scope."""

    bl_idname = "animation_qol.flip_smart"
    bl_label = "Smart Flip"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Paste flipped pose for armatures and mirror non-armature objects by the chosen axis."
    )

    def execute(self, context: Context):
        settings: AnimationQOLSceneSettings | None = getattr(
            context.scene, "animation_qol_settings", None
        )
        if settings is None:
            self.report({"ERROR"}, "Animation QoL settings missing on the scene.")
            return {"CANCELLED"}

        axis_index = _AXIS_TO_INDEX[settings.flip_axis]
        targets = _gather_targets(context, settings)

        if not targets:
            self.report({"WARNING"}, "No targets found for flip operation.")
            return {"CANCELLED"}

        armatures = [obj for obj in targets if obj.type == "ARMATURE"]
        others = [obj for obj in targets if obj.type != "ARMATURE"]

        for armature in armatures:
            obj_utils.armature_paste_flipped(context, armature)

        for obj in others:
            obj_utils.object_flip(obj, axis_index)

        self.report(
            {"INFO"},
            f"Flipped {len(armatures)} armature(s) and {len(others)} object(s) on {settings.flip_axis}.",
        )
        return {"FINISHED"}


class ANIMATIONQOL_OT_flip_pose_only(Operator):
    """Only perform Paste Flipped on armatures in scope."""

    bl_idname = "animation_qol.flip_pose_only"
    bl_label = "Flip Pose"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Paste flipped pose for armatures without touching other objects."

    def execute(self, context: Context):
        settings: AnimationQOLSceneSettings | None = getattr(
            context.scene, "animation_qol_settings", None
        )
        if settings is None:
            self.report({"ERROR"}, "Animation QoL settings missing on the scene.")
            return {"CANCELLED"}

        targets = _gather_targets(context, settings)
        armatures = [obj for obj in targets if obj.type == "ARMATURE"]

        if not armatures:
            self.report({"WARNING"}, "No armatures found in the current scope.")
            return {"CANCELLED"}

        for armature in armatures:
            obj_utils.armature_paste_flipped(context, armature)

        self.report({"INFO"}, f"Flipped pose on {len(armatures)} armature(s).")
        return {"FINISHED"}


class ANIMATIONQOL_OT_flip_objects_only(Operator):
    """Mirror non-armature objects by the configured axis."""

    bl_idname = "animation_qol.flip_objects_only"
    bl_label = "Flip Objects"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Mirror non-armature objects by applying a -1 scale on the chosen axis."

    def execute(self, context: Context):
        settings: AnimationQOLSceneSettings | None = getattr(
            context.scene, "animation_qol_settings", None
        )
        if settings is None:
            self.report({"ERROR"}, "Animation QoL settings missing on the scene.")
            return {"CANCELLED"}

        axis_index = _AXIS_TO_INDEX[settings.flip_axis]
        targets = _gather_targets(context, settings)
        objects = [obj for obj in targets if obj.type != "ARMATURE"]

        if not objects:
            self.report({"WARNING"}, "No non-armature objects found in the current scope.")
            return {"CANCELLED"}

        for obj in objects:
            obj_utils.object_flip(obj, axis_index)

        self.report({"INFO"}, f"Mirrored {len(objects)} object(s) on the {settings.flip_axis} axis.")
        return {"FINISHED"}


CLASSES = (
    ANIMATIONQOL_OT_flip_smart,
    ANIMATIONQOL_OT_flip_pose_only,
    ANIMATIONQOL_OT_flip_objects_only,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)