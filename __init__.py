"""
YABQOLA - Yet Another Blender Quality of Life Add-on
"""

bl_info = {
    "name": "YABQOLA: Yet Another Blender Quality of Life Add-on",
    "description": "Modular animation QoL tools: noise randomizer, timing/stagger, quick flip, and scene cleanup.",
    "author": "Xnom3d",
    "version": (1, 2, 1),
    "blender": (3, 0, 0),
    "location": "Graph/Dope Sheet & 3D View > Sidebar",
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}

import importlib

import bpy

from . import preferences, properties
from .operators import (
    ease_presets,
    keyframe_offset,
    motion_hold,
    noise_randomizer,
    quick_flip,
    render_presets,
    scene_cleanup,
    stagger_timing,
)
from .ui import panels

MODULES = (
    preferences,
    properties,
    noise_randomizer,
    keyframe_offset,
    stagger_timing,
    ease_presets,
    motion_hold,
    quick_flip,
    render_presets,
    scene_cleanup,
    panels,
)


def register():
    for module in MODULES:
        importlib.reload(module)
    for module in MODULES:
        module.register()
    preferences.refresh_keymaps(bpy.context)


def unregister():
    preferences.clear_keymaps()
    for module in reversed(MODULES):
        module.unregister()
