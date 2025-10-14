"""Render configuration helpers for YABQOLA."""

from __future__ import annotations

from typing import Final

import bpy
from bpy.types import Scene

__all__ = ["apply_render_preset"]

_CYCLES_SAMPLE_PRESETS: Final[dict[str, tuple[int, int]]] = {
    "PREVIEW": (64, 32),
    "PLAYBLAST": (128, 64),
    "STILL_DRAFT": (256, 128),
    "STILL_FINAL": (1024, 512),
    "STILL_CLAY": (256, 128),
    "FINAL": (512, 256),
}

_EEVEE_SAMPLE_PRESETS: Final[dict[str, tuple[int, int]]] = {
    "PREVIEW": (16, 8),
    "PLAYBLAST": (32, 16),
    "STILL_DRAFT": (128, 64),
    "STILL_FINAL": (256, 128),
    "STILL_CLAY": (96, 48),
    "FINAL": (64, 32),
}


def _apply_output_settings(scene: Scene, preset: str) -> None:
    """Adjust render output settings for ``preset`` when supported."""

    render = scene.render
    render.use_motion_blur = preset == "FINAL"

    if preset == "PREVIEW":
        render.resolution_percentage = 50
        render.image_settings.file_format = "FFMPEG"
        ffmpeg = render.ffmpeg
        ffmpeg.format = "MPEG4"
        ffmpeg.constant_rate_factor = "MEDIUM"
    elif preset == "PLAYBLAST":
        render.resolution_percentage = 100
        render.image_settings.file_format = "FFMPEG"
        ffmpeg = render.ffmpeg
        ffmpeg.format = "MPEG4"
        ffmpeg.constant_rate_factor = "HIGH"
    elif preset == "STILL_DRAFT":
        render.resolution_percentage = 100
        render.image_settings.file_format = "JPEG"
        render.image_settings.color_mode = "RGB"
        if hasattr(render.image_settings, "quality"):
            render.image_settings.quality = 95
        render.use_motion_blur = False
    elif preset == "STILL_FINAL":
        render.resolution_percentage = 100
        render.image_settings.file_format = "PNG"
        render.image_settings.color_depth = "16"
        render.image_settings.color_mode = "RGBA"
        render.use_motion_blur = False
    elif preset == "STILL_CLAY":
        render.resolution_percentage = 100
        render.image_settings.file_format = "OPEN_EXR"
        render.image_settings.color_depth = "16"
        render.image_settings.color_mode = "RGB"
        render.use_motion_blur = False
    elif preset == "FINAL":
        render.resolution_percentage = 100
        render.image_settings.file_format = "PNG"
        render.image_settings.color_depth = "16"


def _apply_cycles_settings(scene: Scene, preset: str) -> None:
    """Apply Cycles-focused overrides for ``preset`` when Cycles is available."""

    cycles = getattr(scene, "cycles", None)
    if cycles is None:
        return

    samples = _CYCLES_SAMPLE_PRESETS.get(preset)
    if samples:
        render_samples, preview_samples = samples
        try:
            cycles.samples = render_samples
        except Exception:
            pass
        try:
            cycles.preview_samples = preview_samples
        except Exception:
            pass

    if preset == "PREVIEW":
        cycles.use_adaptive_sampling = True
        cycles.use_denoising = False
    elif preset == "PLAYBLAST":
        cycles.use_adaptive_sampling = True
        cycles.use_denoising = True
    elif preset in {"STILL_DRAFT", "STILL_FINAL", "STILL_CLAY", "FINAL"}:
        cycles.use_adaptive_sampling = True
        cycles.use_denoising = True
        cycles.use_preview_denoising = True


def _apply_eevee_settings(scene: Scene, preset: str) -> None:
    """Apply Eevee-focused overrides for ``preset`` when Eevee is available."""

    eevee = getattr(scene, "eevee", None)
    if eevee is None:
        return

    samples = _EEVEE_SAMPLE_PRESETS.get(preset)
    if samples:
        render_samples, preview_samples = samples
        try:
            eevee.taa_render_samples = render_samples
        except Exception:
            pass
        try:
            eevee.taa_samples = preview_samples
        except Exception:
            pass

    if preset == "PREVIEW":
        eevee.use_motion_blur = False
        eevee.use_gtao = False
        eevee.use_ssr = False
    elif preset == "PLAYBLAST":
        eevee.use_motion_blur = False
        eevee.use_gtao = True
        eevee.use_ssr = True
    elif preset in {"STILL_DRAFT", "STILL_FINAL", "STILL_CLAY", "FINAL"}:
        eevee.use_motion_blur = True
        eevee.use_gtao = True
        eevee.use_ssr = True


def apply_render_preset(
    scene: Scene,
    preset: str,
    *,
    adjust_output: bool = True,
    adjust_samples: bool = True,
) -> None:
    """Apply renderer-specific overrides on ``scene`` for the desired ``preset``."""

    if adjust_output:
        _apply_output_settings(scene, preset)

    if adjust_samples:
        _apply_cycles_settings(scene, preset)
        _apply_eevee_settings(scene, preset)

    scene.render.use_simplify = preset in {"PREVIEW", "PLAYBLAST", "STILL_CLAY"}
