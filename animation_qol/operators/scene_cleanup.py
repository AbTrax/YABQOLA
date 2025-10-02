"""Scene cleanup operators for Animation QoL."""

from __future__ import annotations

from typing import Iterable, List

import bpy
from bpy.props import BoolProperty
from bpy.types import Context, Object, Operator

from ..properties import AnimationQOLSceneSettings
from ..utils import objects as obj_utils


_PREVIEW_LIMIT = 8


def _gather_cleanup_targets(
    context: Context,
    settings: AnimationQOLSceneSettings,
) -> List[Object]:
    """Return objects that qualify for deletion according to the cleanup settings."""

    scene = context.scene
    view_layer = context.view_layer
    targets: List[Object] = []

    for obj in scene.objects:
        if obj is None:
            continue

        if settings.cleanup_exclude_linked_data and obj.library:
            continue

        if obj_utils.object_affects_lighting(obj) and settings.cleanup_keep_lights:
            continue

        if obj.type == "CAMERA":
            active_camera = scene.camera
            if settings.cleanup_keep_active_camera and obj == active_camera:
                continue
            if settings.cleanup_keep_cameras:
                continue

        if obj_utils.object_is_visible(
            obj,
            view_layer=view_layer,
            consider_viewport=settings.cleanup_consider_viewport,
            consider_render=settings.cleanup_consider_render,
        ):
            continue

        targets.append(obj)

    return targets


def _format_preview(objects: Iterable[Object]) -> List[str]:
    names = [obj.name for obj in objects]
    if len(names) <= _PREVIEW_LIMIT:
        return names
    slice_names = names[:_PREVIEW_LIMIT]
    slice_names.append(f"… and {len(names) - _PREVIEW_LIMIT} more")
    return slice_names


class ANIMATIONQOL_OT_cleanup_invisible(Operator):
    """Delete objects that are neither visible nor affecting scene lighting."""

    bl_idname = "animation_qol.cleanup_invisible"
    bl_label = "Delete Invisible Objects"
    bl_options = {"REGISTER", "UNDO"}

    dry_run: BoolProperty(
        name="Dry Run",
        description="Report what would be deleted without removing anything",
        default=False,
    )

    _preview_names: List[str]
    _preview_total: int

    def invoke(self, context: Context, event):
        settings: AnimationQOLSceneSettings | None = getattr(
            context.scene, "animation_qol_settings", None
        )
        if settings is None:
            self.report({"ERROR"}, "Animation QoL settings missing on the scene.")
            return {"CANCELLED"}

        candidates = _gather_cleanup_targets(context, settings)
        if not candidates:
            self.report({"INFO"}, "No invisible objects were found.")
            return {"CANCELLED"}

        self._preview_total = len(candidates)
        self._preview_names = _format_preview(candidates)
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context: Context):
        layout = self.layout
        layout.label(text=f"Invisible objects to delete: {self._preview_total}")
        box = layout.box()
        for name in self._preview_names:
            box.label(text=name, icon="DOT")
        layout.prop(self, "dry_run")

    def execute(self, context: Context):
        settings: AnimationQOLSceneSettings | None = getattr(
            context.scene, "animation_qol_settings", None
        )
        if settings is None:
            self.report({"ERROR"}, "Animation QoL settings missing on the scene.")
            return {"CANCELLED"}

        candidates = _gather_cleanup_targets(context, settings)
        if not candidates:
            self.report({"INFO"}, "No invisible objects were found.")
            return {"CANCELLED"}

        if self.dry_run:
            preview = ", ".join(_format_preview(candidates))
            self.report({"INFO"}, f"Dry run: {preview}")
            return {"CANCELLED"}

        obj_count = len(candidates)

        active_obj = context.view_layer.objects.active
        if context.object and context.object.mode != "OBJECT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except Exception:
                pass

        if active_obj in candidates:
            context.view_layer.objects.active = None

        for obj in candidates:
            try:
                if obj.select_get():
                    obj.select_set(False)
            except Exception:
                pass

        for obj in candidates:
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
            except Exception:
                pass

        self.report({"INFO"}, f"Deleted {obj_count} invisible object(s).")
        return {"FINISHED"}


CLASSES = (ANIMATIONQOL_OT_cleanup_invisible,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)