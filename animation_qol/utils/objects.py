"""Object selection and transformation helpers for Animation QoL."""

from __future__ import annotations

from typing import Iterator, List, Sequence

import bpy
from bpy.types import Collection, Context, Object, ViewLayer

__all__ = [
    "armature_paste_flipped",
    "ensure_mode",
    "gather_scope_objects",
    "iter_collection_objects",
    "object_affects_lighting",
    "object_flip",
    "object_is_visible",
]


def iter_collection_objects(collection: Collection | None, include_children: bool = True) -> Iterator[Object]:
    """Yield objects contained in ``collection`` including child collections when requested."""

    if collection is None:
        return

    for obj in collection.objects:
        yield obj

    if not include_children:
        return

    for child in collection.children:
        yield from iter_collection_objects(child, include_children=True)


def _dedupe_objects(objects: Sequence[Object]) -> List[Object]:
    seen: set[int] = set()
    unique: List[Object] = []
    for obj in objects:
        if obj is None:
            continue
        pointer = obj.as_pointer()
        if pointer in seen:
            continue
        seen.add(pointer)
        unique.append(obj)
    return unique


def gather_scope_objects(
    context: Context,
    include_children: bool,
    *,
    scope: str,
    collection: Collection | None,
    include_subcollections: bool,
) -> List[Object]:
    """Return objects defined by the flip scope settings."""

    if scope == "COLLECTION":
        if collection is None:
            objects: List[Object] = []
        else:
            objects = list(
                iter_collection_objects(collection, include_children=include_subcollections)
            )
    else:
        objects = list(getattr(context, "selected_objects", ()))

    if include_children and objects:
        expanded: List[Object] = []
        for obj in objects:
            expanded.extend(obj.children_recursive)
        objects.extend(expanded)

    return _dedupe_objects(objects)


def ensure_mode(context: Context, obj: Object, mode: str) -> str:
    """Switch ``obj`` to ``mode`` returning the previous mode for later restoration."""

    previous = getattr(obj, "mode", "OBJECT")
    view_layer = context.view_layer

    if view_layer.objects.active != obj:
        view_layer.objects.active = obj

    if obj.mode == mode:
        return previous

    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        pass

    view_layer.objects.active = obj

    try:
        bpy.ops.object.mode_set(mode=mode)
    except Exception:
        pass

    return previous


def object_flip(obj: Object, axis_index: int) -> None:
    """Mirror ``obj`` by inverting its local scale on the chosen axis."""

    if obj is None or obj.library or obj.hide_get():
        return

    new_scale = list(obj.scale)
    new_scale[axis_index] *= -1.0
    obj.scale = new_scale


def armature_paste_flipped(context: Context, armature: Object) -> None:
    """Perform Blender's Paste Flipped Pose on ``armature``."""

    if armature.type != "ARMATURE":
        return

    previous_mode = ensure_mode(context, armature, "POSE")

    try:
        pose_bones = armature.pose.bones
        if not any(b.bone.select for b in pose_bones):
            for bone in pose_bones:
                bone.bone.select = True

        bpy.ops.pose.copy()
        bpy.ops.pose.paste(flipped=True)
    except Exception:
        pass
    finally:
        view_layer = context.view_layer
        view_layer.objects.active = armature
        target_mode = previous_mode if previous_mode else "OBJECT"
        try:
            bpy.ops.object.mode_set(mode=target_mode)
        except Exception:
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except Exception:
                pass


def object_is_visible(
    obj: Object,
    *,
    view_layer: ViewLayer,
    consider_viewport: bool,
    consider_render: bool,
) -> bool:
    """Return ``True`` when ``obj`` should be considered visible under the provided criteria."""

    if not consider_render and not consider_viewport:
        return True

    if consider_render and not obj.hide_render:
        return True

    if consider_viewport:
        try:
            if obj.visible_get(view_layer=view_layer):
                return True
        except Exception:
            try:
                if obj.visible_get():
                    return True
            except Exception:
                pass

    return False


def object_affects_lighting(obj: Object) -> bool:
    """Return whether ``obj`` contributes to lighting (lights or light probes)."""

    return obj.type in {"LIGHT", "LIGHT_PROBE"}