"""Reference camera matching operators for YABQOLA."""

from __future__ import annotations

import os
from typing import Optional

import bpy
from bpy import path as bpy_path
from bpy.types import Context, Image, Operator

from ..properties import AnimationQOLSceneSettings
from ..utils import (
    SENSOR_PRESETS,
    crop_factor_from_sensor,
    ensure_active_scene_camera,
    ensure_camera_background_image,
    lens_from_horizontal_fov,
    lens_from_vertical_fov,
    pick_sensor_fit,
    set_render_resolution_from_image,
)

__all__ = [
    "ANIMATIONQOL_OT_refcam_load_image",
    "ANIMATIONQOL_OT_refcam_apply",
]


def _get_settings(context: Context) -> Optional[AnimationQOLSceneSettings]:
    return getattr(context.scene, "animation_qol_settings", None)


def _load_image(path: str) -> Image:
    abspath = bpy_path.abspath(path)
    if not abspath:
        raise FileNotFoundError(path)
    if not os.path.exists(abspath):
        raise FileNotFoundError(abspath)
    return bpy.data.images.load(abspath, check_existing=True)


def _resolve_reference_image(settings: AnimationQOLSceneSettings) -> Image | None:
    if settings.refcam_image:
        return settings.refcam_image
    if settings.refcam_image_path:
        try:
            image = _load_image(settings.refcam_image_path)
        except (FileNotFoundError, RuntimeError):
            return None
        settings.refcam_image = image
        return image
    return None


class ANIMATIONQOL_OT_refcam_load_image(Operator):
    """Load or link a reference image for camera matching."""

    bl_idname = "animation_qol.refcam_load_image"
    bl_label = "Load / Link Image"
    bl_description = "Load the reference image or link an existing datablock"

    def execute(self, context: Context):
        settings = _get_settings(context)
        if settings is None:
            self.report({"ERROR"}, "Scene settings unavailable")
            return {"CANCELLED"}

        path = settings.refcam_image_path.strip()
        if not path:
            self.report({"ERROR"}, "No image path selected")
            return {"CANCELLED"}

        try:
            image = _load_image(path)
        except FileNotFoundError as exc:
            self.report({"ERROR"}, f"Image not found: {exc}")
            return {"CANCELLED"}
        except RuntimeError as exc:
            self.report({"ERROR"}, f"Failed to load image: {exc}")
            return {"CANCELLED"}

        settings.refcam_image = image
        settings.refcam_image_path = image.filepath or bpy_path.abspath(path)

        set_render_resolution_from_image(context.scene, image)
        width, height = image.size
        self.report({"INFO"}, f"Loaded image: {image.name} ({int(width)}x{int(height)})")
        return {"FINISHED"}


class ANIMATIONQOL_OT_refcam_apply(Operator):
    """Match focal length, sensor, and render settings to the reference image."""

    bl_idname = "animation_qol.refcam_apply"
    bl_label = "Match Camera to Reference"
    bl_description = "Apply sensor, fit, focal length, and render resolution"

    def execute(self, context: Context):
        settings = _get_settings(context)
        if settings is None:
            self.report({"ERROR"}, "Scene settings unavailable")
            return {"CANCELLED"}

        if settings.refcam_sensor_preset != "CUSTOM":
            sensor_width, sensor_height, _ = SENSOR_PRESETS[settings.refcam_sensor_preset]
        else:
            sensor_width = settings.refcam_sensor_width
            sensor_height = settings.refcam_sensor_height

        if sensor_width <= 0.0 or sensor_height <= 0.0:
            self.report({"ERROR"}, "Sensor dimensions must be greater than zero")
            return {"CANCELLED"}

        image = _resolve_reference_image(settings)

        camera_object = ensure_active_scene_camera(context)
        camera_data = camera_object.data

        camera_data.sensor_width = sensor_width
        camera_data.sensor_height = sensor_height

        sensor_fit = (
            settings.refcam_sensor_fit
            if settings.refcam_override_fit
            else pick_sensor_fit(image, sensor_width, sensor_height)
        )
        camera_data.sensor_fit = sensor_fit

        try:
            lens_mm = self._compute_lens(settings, sensor_width, sensor_height)
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        camera_data.lens = max(1.0, lens_mm)

        scene = context.scene
        if scene:
            set_render_resolution_from_image(scene, image)

        if settings.refcam_add_background:
            ensure_camera_background_image(camera_data, image)

        self.report(
            {"INFO"},
            f"Matched camera: {sensor_width:.2f}x{sensor_height:.2f} mm, Fit {sensor_fit}, Lens {camera_data.lens:.2f} mm",
        )
        return {"FINISHED"}

    @staticmethod
    def _compute_lens(
        settings: AnimationQOLSceneSettings,
        sensor_width: float,
        sensor_height: float,
    ) -> float:
        if settings.refcam_use_fov_h:
            return lens_from_horizontal_fov(sensor_width, settings.refcam_fov_h_deg)
        if settings.refcam_use_fov_v:
            return lens_from_vertical_fov(sensor_height, settings.refcam_fov_v_deg)
        if settings.refcam_use_equiv_35:
            crop = crop_factor_from_sensor(sensor_width, sensor_height)
            if crop <= 0.0:
                raise ValueError("Invalid crop factor computed from sensor dimensions")
            return settings.refcam_equiv_35_mm / crop
        return settings.refcam_direct_lens_mm


classes = (
    ANIMATIONQOL_OT_refcam_load_image,
    ANIMATIONQOL_OT_refcam_apply,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
