"""Interactive viewport snapping for quickly aligning geometry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import bmesh
import bpy
from bpy.types import Context, Event, Operator
from bpy_extras import view3d_utils
from mathutils import Vector

__all__ = ["ANIMATIONQOL_OT_quick_snap"]

_SNAP_OBJECT_TYPES = {"MESH", "CURVE", "SURFACE", "META", "FONT"}
_SCREEN_THRESHOLD_PX = 14.0


@dataclass(frozen=True)
class _PickInfo:
    location: Vector
    obj: bpy.types.Object | None
    label: str


class ANIMATIONQOL_OT_quick_snap(Operator):
    """Snap the current selection by picking a source and destination point."""

    bl_idname = "animation_qol.quick_snap"
    bl_label = "Quick Snap"
    bl_description = (
        "Pick a source point on the selection and a destination point anywhere in the scene"
    )
    bl_options = {"REGISTER", "UNDO"}

    _stage: str
    _source_point: Vector | None
    _source_label: str
    _area: bpy.types.Area | None
    _region: bpy.types.Region | None
    _rv3d: bpy.types.RegionView3D | None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stage = "SOURCE"
        self._source_point = None
        self._source_label = ""
        self._area = None
        self._region = None
        self._rv3d = None

    # ------------------------------------------------------------------ #
    # Blender operator lifecycle
    # ------------------------------------------------------------------ #
    def invoke(self, context: Context, event: Event):
        if context.area is None or context.area.type != "VIEW_3D":
            self.report({"WARNING"}, "Quick Snap must be started from a 3D Viewport.")
            return {"CANCELLED"}
        if context.region is None or context.region.type != "WINDOW":
            self.report({"WARNING"}, "Invoke Quick Snap from the main viewport region.")
            return {"CANCELLED"}
        if context.mode not in {"OBJECT", "EDIT_MESH"}:
            self.report({"WARNING"}, "Quick Snap currently supports Object and Mesh Edit modes.")
            return {"CANCELLED"}
        if context.mode == "OBJECT" and not context.selected_objects:
            self.report({"WARNING"}, "Select at least one object before running Quick Snap.")
            return {"CANCELLED"}
        if context.mode == "EDIT_MESH" and not self._any_selected_vertices(context):
            self.report({"WARNING"}, "Select vertices to move before running Quick Snap.")
            return {"CANCELLED"}

        self._reset_state(context)

        self._set_header("Quick Snap: pick source point")

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context: Context, event: Event):
        if event.type in {"ESC", "RIGHTMOUSE"}:
            self._clear_header()
            self.report({"INFO"}, "Quick Snap cancelled.")
            return {"CANCELLED"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            result = self._handle_click(context, event)
            if result == "FINISHED":
                self._clear_header()
                return {"FINISHED"}
            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def _reset_state(self, context: Context) -> None:
        self._stage = "SOURCE"
        self._source_point = None
        self._source_label = ""
        self._area = context.area
        self._region = context.region
        self._rv3d = getattr(context.space_data, "region_3d", None)

    # ------------------------------------------------------------------ #
    # Event handling helpers
    # ------------------------------------------------------------------ #
    def _handle_click(self, context: Context, event: Event) -> str:
        restrict_to_selection = self._stage == "SOURCE"
        pick = self._pick_point(context, event, restrict_to_selection)

        if pick is None:
            self.report({"INFO"}, "No valid geometry under the cursor.")
            return "BLOCKED"

        if self._stage == "SOURCE":
            self._source_point = Vector(pick.location)
            self._source_label = pick.label
            self._stage = "DEST"
            self._set_header("Quick Snap: pick destination point")
            self.report({"INFO"}, f"Source set to {pick.label}.")
            return "CONTINUE"

        assert self._source_point is not None
        translation = pick.location - self._source_point

        if translation.length < 1e-6:
            self.report({"INFO"}, "Source and destination are identical. Nothing snapped.")
            return "FINISHED"

        moved = self._apply_translation(context, translation)
        if moved:
            self.report({"INFO"}, f"Snapped selection to {pick.label}.")
        else:
            self.report({"WARNING"}, "No editable geometry was moved.")
        return "FINISHED"

    def _pick_point(
        self,
        context: Context,
        event: Event,
        restrict_to_selection: bool,
    ) -> _PickInfo | None:
        if self._region is None or self._rv3d is None:
            return None

        coord = Vector((event.mouse_region_x, event.mouse_region_y))
        origin = view3d_utils.region_2d_to_origin_3d(self._region, self._rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(self._region, self._rv3d, coord)
        direction.normalize()

        depsgraph = context.evaluated_depsgraph_get()
        hit, location, _normal, face_index, obj, _ = context.scene.ray_cast(
            depsgraph, origin, direction
        )

        if hit and obj is not None:
            if restrict_to_selection and not self._object_in_selection(context, obj):
                return None
            return self._build_pick_info(
                context,
                obj,
                coord,
                location,
                face_index,
                depsgraph,
                restrict_to_selection,
            )

        return self._pick_origin_from_screen(context, coord, restrict_to_selection)

    def _build_pick_info(
        self,
        context: Context,
        obj: bpy.types.Object,
        screen_coord: Vector,
        hit_location: Vector,
        face_index: int,
        depsgraph: bpy.types.Depsgraph,
        restrict_to_selection: bool,
    ) -> _PickInfo:
        if (
            restrict_to_selection
            and context.mode == "EDIT_MESH"
            and obj.type == "MESH"
            and obj.data.is_editmode
        ):
            pick = self._pick_selected_vertex(obj, screen_coord)
            if pick is not None:
                return pick

        vertex_candidate = self._vertex_candidate(obj, screen_coord, face_index, depsgraph)
        origin_candidate = self._origin_candidate(obj, screen_coord)

        candidates: list[tuple[float, _PickInfo]] = []
        if vertex_candidate is not None:
            candidates.append(vertex_candidate)
        if origin_candidate is not None:
            candidates.append(origin_candidate)

        if candidates:
            _dist, info = min(candidates, key=lambda item: item[0])
            return info

        return _PickInfo(location=hit_location, obj=obj, label=f"point on '{obj.name}'")

    def _pick_selected_vertex(
        self,
        obj: bpy.types.Object,
        screen_coord: Vector,
    ) -> _PickInfo | None:
        bm = bmesh.from_edit_mesh(obj.data)
        best_vert: Vector | None = None
        best_dist = float("inf")
        for vert in bm.verts:
            if not vert.select:
                continue
            world_co = obj.matrix_world @ vert.co
            screen_co = view3d_utils.location_3d_to_region_2d(self._region, self._rv3d, world_co)
            if screen_co is None:
                continue
            dist = (screen_co - screen_coord).length
            if dist < best_dist:
                best_dist = dist
                best_vert = world_co

        if best_vert is None:
            return None

        return _PickInfo(
            location=best_vert,
            obj=obj,
            label=f"selected vertex on '{obj.name}'",
        )

    def _vertex_candidate(
        self,
        obj: bpy.types.Object,
        screen_coord: Vector,
        face_index: int,
        depsgraph: bpy.types.Depsgraph,
    ) -> tuple[float, _PickInfo] | None:
        if obj.type not in _SNAP_OBJECT_TYPES:
            return None

        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        if mesh is None:
            return None

        try:
            indices: Sequence[int]
            if 0 <= face_index < len(mesh.polygons):
                indices = mesh.polygons[face_index].vertices
            else:
                indices = range(len(mesh.vertices))

            best_dist = _SCREEN_THRESHOLD_PX
            best_info: _PickInfo | None = None

            for idx in indices:
                world_co = obj.matrix_world @ mesh.vertices[idx].co
                screen_co = view3d_utils.location_3d_to_region_2d(
                    self._region, self._rv3d, world_co
                )
                if screen_co is None:
                    continue
                dist = (screen_co - screen_coord).length
                if dist <= best_dist:
                    best_dist = dist
                    best_info = _PickInfo(
                        location=world_co,
                        obj=obj,
                        label=f"vertex on '{obj.name}'",
                    )

            if best_info is None:
                return None
            return best_dist, best_info
        finally:
            eval_obj.to_mesh_clear()

    def _origin_candidate(
        self,
        obj: bpy.types.Object,
        screen_coord: Vector,
    ) -> tuple[float, _PickInfo] | None:
        origin = obj.matrix_world.translation.copy()
        screen_co = view3d_utils.location_3d_to_region_2d(self._region, self._rv3d, origin)
        if screen_co is None:
            return None

        dist = (screen_co - screen_coord).length
        if dist > _SCREEN_THRESHOLD_PX * 1.2:
            return None
        return dist, _PickInfo(location=origin, obj=obj, label=f"origin of '{obj.name}'")

    def _pick_origin_from_screen(
        self,
        context: Context,
        screen_coord: Vector,
        restrict_to_selection: bool,
    ) -> _PickInfo | None:
        candidates: list[tuple[float, _PickInfo]] = []
        for obj in self._candidate_objects(context, restrict_to_selection):
            origin = obj.matrix_world.translation.copy()
            screen_co = view3d_utils.location_3d_to_region_2d(self._region, self._rv3d, origin)
            if screen_co is None:
                continue
            dist = (screen_co - screen_coord).length
            if dist <= _SCREEN_THRESHOLD_PX * 1.5:
                candidates.append(
                    (dist, _PickInfo(location=origin, obj=obj, label=f"origin of '{obj.name}'"))
                )

        if not candidates:
            return None

        _dist, info = min(candidates, key=lambda item: item[0])
        return info

    # ------------------------------------------------------------------ #
    # Selection helpers
    # ------------------------------------------------------------------ #
    def _candidate_objects(self, context: Context, restrict: bool) -> Iterable[bpy.types.Object]:
        if context.mode == "OBJECT":
            if restrict:
                return tuple(obj for obj in context.selected_objects if obj.visible_get())
            return tuple(obj for obj in context.view_layer.objects if obj.visible_get())
        if context.mode == "EDIT_MESH":
            return self._iter_edit_objects(context)
        return tuple()

    def _iter_edit_objects(self, context: Context) -> Iterable[bpy.types.Object]:
        objects = getattr(context, "objects_in_mode_unique_data", None)
        if objects:
            return tuple(obj for obj in objects if obj.type == "MESH" and obj.data.is_editmode)
        edit_obj = context.edit_object
        if edit_obj and edit_obj.type == "MESH" and edit_obj.data.is_editmode:
            return (edit_obj,)
        return tuple()

    def _any_selected_vertices(self, context: Context) -> bool:
        for obj in self._iter_edit_objects(context):
            bm = bmesh.from_edit_mesh(obj.data)
            if any(vert.select for vert in bm.verts):
                return True
        return False

    def _object_in_selection(self, context: Context, obj: bpy.types.Object) -> bool:
        if context.mode == "OBJECT":
            return obj in context.selected_objects
        if context.mode == "EDIT_MESH":
            return obj in self._iter_edit_objects(context)
        return False

    # ------------------------------------------------------------------ #
    # Transform helpers
    # ------------------------------------------------------------------ #
    def _apply_translation(self, context: Context, translation: Vector) -> bool:
        if context.mode == "OBJECT":
            for obj in context.selected_objects:
                obj.location += translation
            return bool(context.selected_objects)

        if context.mode == "EDIT_MESH":
            moved = False
            for obj in self._iter_edit_objects(context):
                bm = bmesh.from_edit_mesh(obj.data)
                selected_verts = [vert for vert in bm.verts if vert.select]
                if not selected_verts:
                    continue
                local_translation = self._world_to_local_vector(obj, translation)
                for vert in selected_verts:
                    vert.co += local_translation
                bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)
                moved = True
            return moved

        return False

    @staticmethod
    def _world_to_local_vector(obj: bpy.types.Object, vector: Vector) -> Vector:
        matrix = obj.matrix_world.inverted_safe().to_3x3()
        return matrix @ vector

    # ------------------------------------------------------------------ #
    # UI helpers
    # ------------------------------------------------------------------ #
    def _set_header(self, message: str) -> None:
        if self._area is not None:
            self._area.header_text_set(message)

    def _clear_header(self) -> None:
        if self._area is not None:
            self._area.header_text_set(None)


CLASSES = (ANIMATIONQOL_OT_quick_snap,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
