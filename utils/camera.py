"""Camera utilities for YABQOLA's reference matching tools."""

from __future__ import annotations

import math

import bpy
from bpy.types import Camera, Context, Image, Object, Scene

SENSOR_PRESETS: dict[str, tuple[float, float, str]] = {
    "FULL_FRAME": (36.0, 24.0, "Full Frame 36×24 mm"),
    "APS_C": (23.6, 15.7, "APS-C 23.6×15.7 mm"),
    "MFT": (17.3, 13.0, "Micro Four Thirds 17.3×13.0 mm"),
    "SUPER35": (24.89, 18.66, "Super35 (Arri) 24.89×18.66 mm"),
    "1_INCH": (13.2, 8.8, '1" type 13.2×8.8 mm'),
    "IPHONE12_MAIN": (5.6, 4.2, 'Phone Main ~1/1.76" (~5.6×4.2 mm)'),
}

DIAGONAL_35MM = math.hypot(36.0, 24.0)

__all__ = [
    "SENSOR_PRESETS",
    "DIAGONAL_35MM",
    "ensure_active_scene_camera",
    "ensure_camera_background_image",
    "set_render_resolution_from_image",
    "pick_sensor_fit",
    "crop_factor_from_sensor",
    "lens_from_horizontal_fov",
    "lens_from_vertical_fov",
]


def ensure_active_scene_camera(context: Context) -> Object:
    """Return the active camera object, creating one if missing."""
    scene = context.scene
    if scene is None:
        raise RuntimeError("No active scene available")

    cam_obj = scene.camera
    if cam_obj and cam_obj.type == "CAMERA":
        return cam_obj

    camera_data = bpy.data.cameras.new("YABQOLA RefCam")
    camera_object = bpy.data.objects.new(camera_data.name, camera_data)
    root_collection = scene.collection or context.collection
    if root_collection is None:
        raise RuntimeError("Unable to access scene root collection")
    root_collection.objects.link(camera_object)
    scene.camera = camera_object
    return camera_object


def ensure_camera_background_image(
    camera_data: Camera,
    image: Image | None,
    *,
    tag: str = "[YABQOLA RefCam]",
):
    """Attach a tagged background image slot to the camera."""
    if image is None:
        return None

    # Remove previous background entries created by this tool.
    slots_to_remove = [
        idx
        for idx, slot in enumerate(camera_data.background_images)
        if slot.image and slot.image.name.endswith(tag)
    ]
    for idx in reversed(slots_to_remove):
        camera_data.background_images.remove(camera_data.background_images[idx])

    camera_data.show_background_images = True
    slot = camera_data.background_images.new()

    display_image = image
    tagged_name = f"{image.name} {tag}"
    if image.name.endswith(tag):
        tagged_name = image.name
    elif tagged_name in bpy.data.images:
        display_image = bpy.data.images[tagged_name]
    else:
        display_image = image.copy()
        display_image.name = tagged_name

    slot.image = display_image
    slot.alpha = 0.7
    slot.display_depth = "BACK"
    slot.frame_method = "CROP"
    return slot


def set_render_resolution_from_image(scene: Scene, image: Image | None) -> None:
    """Sync render resolution to match the reference image dimensions."""
    if image is None:
        return
    width, height = image.size
    if width <= 0 or height <= 0:
        return
    render = scene.render
    render.resolution_x = width
    render.resolution_y = height
    render.resolution_percentage = 100
    render.pixel_aspect_x = 1.0
    render.pixel_aspect_y = 1.0


def pick_sensor_fit(image: Image | None, sensor_width: float, sensor_height: float) -> str:
    """Return the preferred sensor fit based on image and sensor aspect ratio."""
    if image is None:
        return "HORIZONTAL"

    width, height = image.size
    if width <= 0 or height <= 0:
        return "HORIZONTAL"

    image_aspect = width / height
    sensor_aspect = sensor_width / sensor_height if sensor_height else 1.0
    return "HORIZONTAL" if image_aspect >= sensor_aspect else "VERTICAL"


def crop_factor_from_sensor(sensor_width: float, sensor_height: float) -> float:
    """Calculate the diagonal crop factor relative to the 35 mm reference sensor."""
    diagonal = math.hypot(sensor_width, sensor_height)
    if diagonal <= 0:
        return 1.0
    return DIAGONAL_35MM / diagonal


def lens_from_horizontal_fov(sensor_width: float, fov_degrees: float) -> float:
    """Convert a horizontal field of view to focal length in millimetres."""
    if fov_degrees <= 0 or fov_degrees >= 180.0:
        raise ValueError("Horizontal FOV must be within (0, 180) degrees")
    return sensor_width / (2.0 * math.tan(math.radians(fov_degrees) * 0.5))


def lens_from_vertical_fov(sensor_height: float, fov_degrees: float) -> float:
    """Convert a vertical field of view to focal length in millimetres."""
    if fov_degrees <= 0 or fov_degrees >= 180.0:
        raise ValueError("Vertical FOV must be within (0, 180) degrees")
    return sensor_height / (2.0 * math.tan(math.radians(fov_degrees) * 0.5))
