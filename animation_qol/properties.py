"""Property definitions for the Animation QoL add-on."""

from __future__ import annotations

import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty, PointerProperty
from bpy.types import PropertyGroup, Scene


class AnimationQOLSceneSettings(PropertyGroup):
    """Persistent settings exposed in the UI panels."""

    noise_seed: IntProperty(
        name="Seed",
        description="Seed for random operations (0 uses system entropy)",
        default=0,
        min=0,
    )
    noise_phase_min: FloatProperty(
        name="Phase Min",
        description="Lower bound for randomized noise phase",
        default=0.0,
        soft_min=-50.0,
        soft_max=50.0,
    )
    noise_phase_max: FloatProperty(
        name="Phase Max",
        description="Upper bound for randomized noise phase",
        default=6.283,
        soft_min=-50.0,
        soft_max=50.0,
    )
    noise_offset_min: FloatProperty(
        name="Offset Min",
        description="Lower bound for randomized noise offset",
        default=-5.0,
        soft_min=-250.0,
        soft_max=250.0,
    )
    noise_offset_max: FloatProperty(
        name="Offset Max",
        description="Upper bound for randomized noise offset",
        default=5.0,
        soft_min=-250.0,
        soft_max=250.0,
    )
    noise_strength_min: FloatProperty(
        name="Strength Min",
        description="Lower bound for randomized noise strength",
        default=0.1,
        min=0.0,
        soft_max=5.0,
    )
    noise_strength_max: FloatProperty(
        name="Strength Max",
        description="Upper bound for randomized noise strength",
        default=1.0,
        min=0.0,
        soft_max=5.0,
    )
    noise_scale_min: FloatProperty(
        name="Scale Min",
        description="Lower bound for randomized noise scale",
        default=3.0,
        min=0.001,
        soft_max=100.0,
    )
    noise_scale_max: FloatProperty(
        name="Scale Max",
        description="Upper bound for randomized noise scale",
        default=18.0,
        min=0.001,
        soft_max=100.0,
    )
    noise_create_missing: BoolProperty(
        name="Create Missing",
        description="Create a noise modifier when one is not present on a curve",
        default=True,
    )

    keyframe_frame_offset: IntProperty(
        name="Frame Offset",
        description="Number of frames to shift keyframes by",
        default=2,
        soft_min=-250,
        soft_max=250,
        step=1,
    )
    keyframe_only_selected_keys: BoolProperty(
        name="Only Selected Keys",
        description="Move only selected keys instead of entire curves",
        default=True,
    )

    stagger_step: IntProperty(
        name="Step",
        description="Frame offset increment per object when staggering",
        default=3,
        soft_min=-250,
        soft_max=250,
        step=1,
    )
    stagger_selected_only: BoolProperty(
        name="Selected Keys Only",
        description="When enabled, only selected keys are staggered",
        default=True,
    )
    stagger_reverse_order: BoolProperty(
        name="Reverse Order",
        description="Apply staggering in reverse object selection order",
        default=False,
    )
    stagger_include_shape_keys: BoolProperty(
        name="Shape Keys",
        description="Include shape key animations in the stagger operation",
        default=True,
    )


CLASSES = (AnimationQOLSceneSettings,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    Scene.animation_qol_settings = PointerProperty(type=AnimationQOLSceneSettings)


def unregister():
    del Scene.animation_qol_settings
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)