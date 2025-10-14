"""Quick snap render helper for still captures."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import bpy
from bpy.types import Context, Operator

from ..properties import AnimationQOLSceneSettings
from ..utils.render import apply_render_preset

__all__ = ["ANIMATIONQOL_OT_quick_snap"]

_EXTENSION_MAP: dict[str, str] = {
    "BMP": "bmp",
    "IRIS": "rgb",
    "PNG": "png",
    "JPEG": "jpg",
    "JPEG2000": "jp2",
    "TIFF": "tif",
    "OPEN_EXR": "exr",
    "OPEN_EXR_MULTILAYER": "exr",
    "TARGA": "tga",
    "TARGA_RAW": "tga",
    "CINEON": "cin",
    "DPX": "dpx",
    "HDR": "hdr",
}


@dataclass
class _RenderState:
    filepath: str
    resolution_percentage: int
    use_stamp: bool
    use_simplify: bool
    image_settings: dict[str, object]
    ffmpeg_settings: dict[str, object]
    cycles_settings: dict[str, object] | None
    eevee_settings: dict[str, object] | None
    camera: bpy.types.Object | None


def _capture_render_state(scene: bpy.types.Scene) -> _RenderState:
    render = scene.render
    image_settings = render.image_settings
    ffmpeg_settings = getattr(render, "ffmpeg", None)
    cycles = getattr(scene, "cycles", None)
    eevee = getattr(scene, "eevee", None)

    return _RenderState(
        filepath=str(render.filepath),
        resolution_percentage=int(render.resolution_percentage),
        use_stamp=bool(render.use_stamp),
        use_simplify=bool(render.use_simplify),
        image_settings={
            "file_format": getattr(image_settings, "file_format", None),
            "color_depth": getattr(image_settings, "color_depth", None),
            "color_mode": getattr(image_settings, "color_mode", None),
            "quality": getattr(image_settings, "quality", None),
        },
        ffmpeg_settings={
            "format": getattr(ffmpeg_settings, "format", None) if ffmpeg_settings else None,
            "constant_rate_factor": getattr(ffmpeg_settings, "constant_rate_factor", None)
            if ffmpeg_settings
            else None,
        },
        cycles_settings={
            "samples": getattr(cycles, "samples", None),
            "preview_samples": getattr(cycles, "preview_samples", None),
            "use_adaptive_sampling": getattr(cycles, "use_adaptive_sampling", None),
            "use_denoising": getattr(cycles, "use_denoising", None),
            "use_preview_denoising": getattr(cycles, "use_preview_denoising", None),
        }
        if cycles
        else None,
        eevee_settings={
            "taa_render_samples": getattr(eevee, "taa_render_samples", None),
            "taa_samples": getattr(eevee, "taa_samples", None),
            "use_motion_blur": getattr(eevee, "use_motion_blur", None),
            "use_gtao": getattr(eevee, "use_gtao", None),
            "use_ssr": getattr(eevee, "use_ssr", None),
        }
        if eevee
        else None,
        camera=scene.camera,
    )


def _restore_render_state(scene: bpy.types.Scene, state: _RenderState) -> None:
    render = scene.render
    render.filepath = state.filepath
    render.resolution_percentage = state.resolution_percentage
    render.use_stamp = state.use_stamp
    render.use_simplify = state.use_simplify

    image_settings = render.image_settings
    for key, value in state.image_settings.items():
        if value is None:
            continue
        try:
            setattr(image_settings, key, value)
        except AttributeError:
            continue

    ffmpeg_settings = getattr(render, "ffmpeg", None)
    if ffmpeg_settings:
        for key, value in state.ffmpeg_settings.items():
            if value is None:
                continue
            try:
                setattr(ffmpeg_settings, key, value)
            except AttributeError:
                continue

    cycles = getattr(scene, "cycles", None)
    if cycles and state.cycles_settings:
        for key, value in state.cycles_settings.items():
            if value is None:
                continue
            try:
                setattr(cycles, key, value)
            except AttributeError:
                continue

    eevee = getattr(scene, "eevee", None)
    if eevee and state.eevee_settings:
        for key, value in state.eevee_settings.items():
            if value is None:
                continue
            try:
                setattr(eevee, key, value)
            except AttributeError:
                continue

    scene.camera = state.camera


def _resolve_base_path(scene: bpy.types.Scene, settings: AnimationQOLSceneSettings) -> Path:
    directory = settings.quick_snap_directory.strip()
    if not directory:
        directory = "//quick_snaps"
    abs_path = Path(bpy.path.abspath(directory))
    abs_path.mkdir(parents=True, exist_ok=True)
    return abs_path


def _build_filename(settings: AnimationQOLSceneSettings, frame: int) -> str:
    prefix = settings.quick_snap_filename_prefix.strip() or "snap"
    suffix_parts: list[str] = []

    if settings.quick_snap_append_frame:
        suffix_parts.append(f"f{frame:04d}")

    if settings.quick_snap_append_timestamp:
        suffix_parts.append(datetime.now().strftime("%Y%m%d_%H%M%S"))

    suffix = "_".join(suffix_parts)
    return f"{prefix}_{suffix}" if suffix else prefix


class ANIMATIONQOL_OT_quick_snap(Operator):
    """Render a quick still using the configured preset and output options."""

    bl_idname = "animation_qol.quick_snap"
    bl_label = "Quick Snap"
    bl_description = "Render a still image with the configured snap settings and save it automatically"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context):
        scene = context.scene
        settings: AnimationQOLSceneSettings | None = getattr(
            scene, "animation_qol_settings", None
        )
        if settings is None:
            self.report({"WARNING"}, "Animation QoL settings unavailable on this scene.")
            return {"CANCELLED"}

        render = scene.render
        state = _capture_render_state(scene)

        base_path = _resolve_base_path(scene, settings)
        filename = _build_filename(settings, context.scene.frame_current)
        render.filepath = str(base_path / filename)

        if settings.quick_snap_use_preset:
            apply_render_preset(
                scene,
                settings.render_preset,
                adjust_output=settings.render_adjust_output,
                adjust_samples=settings.render_adjust_samples,
            )

        if settings.quick_snap_use_custom_resolution:
            render.resolution_percentage = settings.quick_snap_resolution_percentage

        render.use_stamp = settings.quick_snap_apply_stamp

        if settings.quick_snap_camera and settings.quick_snap_camera.type == "CAMERA":
            scene.camera = settings.quick_snap_camera

        try:
            result = bpy.ops.render.render(write_still=True)
            if "FINISHED" not in result:
                _restore_render_state(scene, state)
                self.report({"WARNING"}, "Quick snap cancelled.")
                return {"CANCELLED"}
        except Exception as exc:  # pragma: no cover - safety guard for Blender runtime
            _restore_render_state(scene, state)
            self.report({"ERROR"}, f"Quick snap failed: {exc}")
            return {"CANCELLED"}

        snap_format = render.image_settings.file_format
        _restore_render_state(scene, state)

        extension = _EXTENSION_MAP.get(snap_format, snap_format.lower())
        final_path = base_path / f"{filename}.{extension}"
        self.report({"INFO"}, f"Quick snap saved to: {final_path}")
        return {"FINISHED"}


CLASSES = (ANIMATIONQOL_OT_quick_snap,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
