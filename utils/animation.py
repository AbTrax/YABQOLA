"""Animation data helpers used across operators."""

from __future__ import annotations

from typing import Iterable, List, Sequence

import bpy
from bpy.types import Context, FCurve, Object

__all__ = [
    "gather_target_fcurves",
    "iter_fcurves_for_object",
    "shift_keyframes",
    "sorted_range",
]


def _fcurve_key(fcurve: FCurve) -> tuple:
    id_data = fcurve.id_data
    pointer = id_data.as_pointer() if id_data else id(fcurve)
    return (pointer, fcurve.data_path, fcurve.array_index)


def iter_fcurves_for_object(obj: Object | None, *, include_shape_keys: bool = True) -> Iterable[FCurve]:
    """Yield fcurves associated with an object, optionally including shape keys."""

    if obj is None:
        return []

    anim_data = obj.animation_data
    if anim_data and anim_data.action:
        for fcurve in anim_data.action.fcurves:
            yield fcurve

    if include_shape_keys:
        data = getattr(obj, "data", None)
        shape_keys = getattr(data, "shape_keys", None)
        if shape_keys:
            sk_data = shape_keys.animation_data
            if sk_data and sk_data.action:
                for fcurve in sk_data.action.fcurves:
                    yield fcurve


def gather_target_fcurves(
    context: Context,
    *,
    only_selected_curves: bool = True,
    include_shape_keys: bool = True,
) -> List[FCurve]:
    """Collect fcurves to operate on based on the current selection."""

    result: List[FCurve] = []
    seen: set[tuple] = set()

    selected_editable = getattr(context, "selected_editable_fcurves", None)
    if selected_editable:
        for fcurve in selected_editable:
            if getattr(fcurve, "lock", False):
                continue
            key = _fcurve_key(fcurve)
            if key in seen:
                continue
            result.append(fcurve)
            seen.add(key)

    if result and only_selected_curves:
        return result

    objects: Sequence[Object] = tuple(getattr(context, "selected_objects", ()))
    active = getattr(context, "active_object", None)

    if active and active not in objects:
        objects = (*objects, active)

    for obj in objects:
        for fcurve in iter_fcurves_for_object(obj, include_shape_keys=include_shape_keys):
            if getattr(fcurve, "lock", False):
                continue
            key = _fcurve_key(fcurve)
            if key in seen:
                continue
            result.append(fcurve)
            seen.add(key)

    return result


def shift_keyframes(fcurve: FCurve, frame_delta: float, only_selected: bool = True) -> int:
    """Shift keyframes on ``fcurve`` by ``frame_delta`` frames.

    Parameters
    ----------
    fcurve: FCurve
        The animation curve to edit.
    frame_delta: float
        Amount of frames to move the keyframes by.
    only_selected: bool, optional
        When True (default) only selected keyframes move.

    Returns
    -------
    int
        Number of keyframes that were shifted.
    """

    moved = 0
    for key_point in fcurve.keyframe_points:
        if only_selected and not key_point.select_control_point:
            continue
        key_point.co.x += frame_delta
        key_point.handle_left.x += frame_delta
        key_point.handle_right.x += frame_delta
        moved += 1

    if moved:
        fcurve.update()

    return moved


def sorted_range(value_a: float, value_b: float) -> tuple[float, float]:
    """Return the provided values sorted as a range."""

    return (value_a, value_b) if value_a <= value_b else (value_b, value_a)