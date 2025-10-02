"""Noise modifier randomization operator."""

from __future__ import annotations

import random

import bpy
from bpy.props import BoolProperty
from bpy.types import Context, FCurve, Operator

from ..properties import AnimationQOLSceneSettings
from ..utils.animation import gather_target_fcurves, sorted_range


class ANIMATIONQOL_OT_randomize_noise_modifiers(Operator):
    """Randomize parameters for noise modifiers across multiple curves."""

    bl_idname = "animation_qol.randomize_noise_modifiers"
    bl_label = "Randomize Noise"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Randomize the phase, offset, strength, and scale of noise modifiers "
        "across the current selection. Optionally creates missing modifiers."
    )

    include_only_selected_curves: BoolProperty(
        name="Only Selected Curves",
        description="Limit the operation to curves selected in the Graph Editor",
        default=True,
    )

    def execute(self, context: Context):
        settings: AnimationQOLSceneSettings | None = getattr(
            context.scene, "animation_qol_settings", None
        )
        if settings is None:
            self.report({"ERROR"}, "YABQOLA settings missing on the scene.")
            return {"CANCELLED"}

        fcurves = gather_target_fcurves(
            context,
            only_selected_curves=self.include_only_selected_curves,
        )
        if not fcurves:
            self.report({"WARNING"}, "No F-Curves found to update.")
            return {"CANCELLED"}

        phase_min, phase_max = sorted_range(settings.noise_phase_min, settings.noise_phase_max)
        offset_min, offset_max = sorted_range(settings.noise_offset_min, settings.noise_offset_max)
        strength_min, strength_max = sorted_range(
            settings.noise_strength_min, settings.noise_strength_max
        )
        scale_min, scale_max = sorted_range(settings.noise_scale_min, settings.noise_scale_max)

        seed = int(settings.noise_seed)
        if seed > 0:
            random.seed(seed)
        else:
            random.seed()

        created = 0
        affected = 0

        for fcurve in fcurves:
            modifiers = [mod for mod in fcurve.modifiers if mod.type == "NOISE"]
            if not modifiers and settings.noise_create_missing:
                mod = fcurve.modifiers.new(type="NOISE")
                # Provide initial values before randomization so the curve updates nicely.
                mod.strength = strength_max
                mod.scale = max(0.001, scale_min)
                modifiers.append(mod)
                created += 1

            if not modifiers:
                continue

            for modifier in modifiers:
                modifier.phase = random.uniform(phase_min, phase_max)
                modifier.offset = random.uniform(offset_min, offset_max)
                modifier.strength = random.uniform(strength_min, strength_max)
                modifier.scale = max(0.001, random.uniform(scale_min, scale_max))
                affected += 1

        if affected == 0:
            self.report({"WARNING"}, "Nothing to randomize. Add noise modifiers first.")
            return {"CANCELLED"}

        self.report(
            {"INFO"},
            f"Randomized {affected} modifiers." + (f" Created {created}." if created else ""),
        )
        return {"FINISHED"}


CLASSES = (ANIMATIONQOL_OT_randomize_noise_modifiers,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)