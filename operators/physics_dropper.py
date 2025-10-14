"""Physics dropper operator that ray casts objects onto ground geometry."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

import bpy
from bpy.types import Context, Object, Operator
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from ..properties import AnimationQOLSceneSettings
from ..utils.objects import iter_collection_objects

__all__ = ["ANIMATIONQOL_OT_drop_to_surface"]


def _gather_ground_objects(
    scene: bpy.types.Scene,
    settings: AnimationQOLSceneSettings,
    *,
    drop_ids: set[int],
) -> List[Object]:
    if settings.drop_collision_collection:
        return [
            obj
            for obj in iter_collection_objects(
                settings.drop_collision_collection, include_children=settings.drop_include_subcollections
            )
            if obj and obj.type == "MESH"
        ]

    return [
        obj for obj in scene.objects if obj.as_pointer() not in drop_ids and obj.type == "MESH"
    ]


def _build_bvh_tree(
    objects: Sequence[Object],
    depsgraph: bpy.types.Depsgraph,
) -> BVHTree | None:
    if not objects:
        return None

    vertices: List[Vector] = []
    polygons: List[Tuple[int, ...]] = []
    offset = 0

    for obj in objects:
        if obj.type != "MESH":
            continue
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        if mesh is None:
            continue

        world_matrix = obj.matrix_world
        for vertex in mesh.vertices:
            vertices.append(world_matrix @ vertex.co)
        for poly in mesh.polygons:
            polygons.append(tuple(vertex_index + offset for vertex_index in poly.vertices))
        offset += len(mesh.vertices)
        eval_obj.to_mesh_clear()

    if not polygons:
        return None

    return BVHTree.FromPolygons(vertices, polygons, all_triangles=False)


def _bottom_corners(obj: Object) -> Iterable[Vector]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    if not corners:
        return []
    min_z = min(corner.z for corner in corners)
    epsilon = 1e-5
    for corner in corners:
        if corner.z - min_z <= epsilon:
            yield corner


class ANIMATIONQOL_OT_drop_to_surface(Operator):
    """Drop selected objects onto the ground using ray casting."""

    bl_idname = "animation_qol.drop_to_surface"
    bl_label = "Physics Dropper"
    bl_description = (
        "Cast the selected objects downward, aligning them to the first collision surface that is found"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        settings: AnimationQOLSceneSettings | None = getattr(
            context.scene, "animation_qol_settings", None
        )
        if settings is None:
            self.report({"WARNING"}, "Animation QoL settings unavailable on this scene.")
            return {"CANCELLED"}

        candidates: Sequence[Object] = tuple(getattr(context, "selected_editable_objects", ()))
        if not candidates:
            candidates = tuple(context.selected_objects)

        drop_targets = [
            obj
            for obj in candidates
            if obj.type in {"MESH", "CURVE", "SURFACE", "FONT", "META", "GPENCIL", "EMPTY"}
        ]
        if not drop_targets:
            self.report({"INFO"}, "No supported objects selected for dropping.")
            return {"CANCELLED"}

        drop_ids = {obj.as_pointer() for obj in drop_targets}
        ground_objects = _gather_ground_objects(context.scene, settings, drop_ids=drop_ids)
        if not ground_objects:
            self.report({"WARNING"}, "No collision geometry found for the drop operation.")
            return {"CANCELLED"}

        depsgraph = context.evaluated_depsgraph_get()
        bvh = _build_bvh_tree(ground_objects, depsgraph)
        if bvh is None:
            self.report({"WARNING"}, "Unable to build collision data from the provided objects.")
            return {"CANCELLED"}

        ray_direction = Vector((0.0, 0.0, -1.0))
        move_count = 0
        align_count = 0

        for obj in drop_targets:
            min_drop = None
            best_normal = None

            for corner in _bottom_corners(obj):
                origin = corner + Vector((0.0, 0.0, settings.drop_ray_offset))
                max_distance = settings.drop_max_distance + settings.drop_ray_offset + 0.1
                location, normal, _index, _distance = bvh.ray_cast(origin, ray_direction, max_distance)
                if location is None:
                    continue

                distance_to_surface = corner.z - (location.z + settings.drop_contact_offset)
                if distance_to_surface <= 1e-6:
                    continue

                if min_drop is None or distance_to_surface < min_drop:
                    min_drop = distance_to_surface
                    best_normal = normal

            if min_drop is None:
                continue

            new_matrix = obj.matrix_world.copy()
            new_matrix.translation -= Vector((0.0, 0.0, min_drop))
            obj.matrix_world = new_matrix
            move_count += 1

            if settings.drop_align_rotation and best_normal is not None and best_normal.length > 0.0:
                best_normal.normalize()
                current_up = (obj.matrix_world.to_quaternion() @ Vector((0.0, 0.0, 1.0))).normalized()
                try:
                    delta = current_up.rotation_difference(best_normal)
                except ZeroDivisionError:
                    delta = None

                if delta is not None:
                    target_quaternion = delta @ obj.matrix_world.to_quaternion()
                    if obj.rotation_mode == "QUATERNION":
                        obj.rotation_quaternion = target_quaternion
                    else:
                        obj.rotation_euler = target_quaternion.to_euler(obj.rotation_mode)
                    align_count += 1

        if move_count == 0:
            self.report({"INFO"}, "No objects required dropping based on the current settings.")
            return {"CANCELLED"}

        if settings.drop_align_rotation and align_count:
            self.report(
                {"INFO"},
                f"Dropped {move_count} object(s) and aligned {align_count} to surface normals.",
            )
        else:
            self.report({"INFO"}, f"Dropped {move_count} object(s) onto the ground.")

        return {"FINISHED"}


CLASSES = (ANIMATIONQOL_OT_drop_to_surface,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
