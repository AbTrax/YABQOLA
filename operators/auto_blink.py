"""Automatic blink generation for shape key driven rigs."""

from __future__ import annotations

import random

import bpy
from bpy.types import Context, Object, Operator

from ..properties import AnimationQOLSceneSettings

__all__ = ["ANIMATIONQOL_OT_generate_auto_blinks"]


def _iter_target_objects(context: Context, settings: AnimationQOLSceneSettings) -> list[Object]:
    if settings.blink_use_selected_objects:
        return [obj for obj in context.selected_objects if getattr(obj.data, "shape_keys", None)]
    return [obj for obj in context.scene.objects if getattr(obj.data, "shape_keys", None)]


def _insert_keyframe(block: bpy.types.ShapeKey, value: float, frame: int) -> None:
    block.value = value
    block.keyframe_insert("value", frame=frame)


class ANIMATIONQOL_OT_generate_auto_blinks(Operator):
    """Create randomized blink animations on selected shape keys."""

    bl_idname = "animation_qol.generate_auto_blinks"
    bl_label = "Generate Auto Blinks"
    bl_description = "Generate blink keyframes on the target shape key across the configured frame range"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        settings: AnimationQOLSceneSettings | None = getattr(
            context.scene, "animation_qol_settings", None
        )
        if settings is None:
            self.report({"WARNING"}, "Animation QoL settings unavailable on this scene.")
            return {"CANCELLED"}

        frame_start = min(settings.blink_frame_start, settings.blink_frame_end)
        frame_end = max(settings.blink_frame_start, settings.blink_frame_end)
        interval = max(1, settings.blink_interval)
        randomness = max(0, settings.blink_interval_random)
        close_frames = max(1, settings.blink_close_frames)
        open_frames = max(1, settings.blink_open_frames)
        hold_frames = max(0, settings.blink_hold_frames)
        blink_length = close_frames + hold_frames + open_frames

        rng = random.Random()
        if settings.blink_seed > 0:
            rng.seed(settings.blink_seed)

        targets = _iter_target_objects(context, settings)
        if not targets:
            self.report({"INFO"}, "No objects with shape keys were found for blink generation.")
            return {"CANCELLED"}

        shape_key_name = settings.blink_shape_key_name.strip()
        if not shape_key_name:
            self.report({"WARNING"}, "Shape key name is empty.")
            return {"CANCELLED"}

        processed = 0
        missing = []

        for obj in targets:
            shape_keys = getattr(obj.data, "shape_keys", None)
            blocks = getattr(shape_keys, "key_blocks", None) if shape_keys else None
            key_block = blocks.get(shape_key_name) if blocks else None
            if key_block is None:
                missing.append(obj.name)
                continue

            # Ensure baseline value
            _insert_keyframe(key_block, 0.0, frame_start)
            _insert_keyframe(key_block, 0.0, frame_end + 1)

            current_frame = frame_start
            blink_count = 0

            while current_frame + blink_length <= frame_end:
                blink_start = current_frame
                close_end = blink_start + close_frames
                hold_end = close_end + hold_frames
                open_end = hold_end + open_frames

                _insert_keyframe(key_block, 0.0, max(frame_start, blink_start - 1))
                _insert_keyframe(key_block, settings.blink_strength, close_end)
                if hold_frames:
                    _insert_keyframe(key_block, settings.blink_strength, hold_end)
                _insert_keyframe(key_block, 0.0, open_end)

                blink_count += 1

                interval_variation = rng.randint(-randomness, randomness) if randomness else 0
                next_gap = max(1, interval + interval_variation)
                current_frame = open_end + next_gap

            if blink_count:
                processed += 1

        if processed == 0:
            if missing:
                missing_str = ", ".join(missing[:5])
                more = "" if len(missing) <= 5 else "..."
                self.report({"WARNING"}, f"No blinks created. Missing shape key on: {missing_str}{more}")
            else:
                self.report({"WARNING"}, "No blinks were generated within the provided frame range.")
            return {"CANCELLED"}

        if missing:
            missing_str = ", ".join(missing[:5])
            more = "" if len(missing) <= 5 else "..."
            self.report(
                {"INFO"},
                f"Generated blinks for {processed} object(s). Missing shape key on: {missing_str}{more}",
            )
        else:
            self.report({"INFO"}, f"Generated blinks for {processed} object(s).")

        return {"FINISHED"}


CLASSES = (ANIMATIONQOL_OT_generate_auto_blinks,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
