"""
Animation QoL Add-on Package
"""

bl_info = {
    "name": "Animation QoL Toolkit",
    "description": "Modular tools to streamline animation workflows with noise randomization, timing, quick flip, and cleanup utilities.",
    "author": "Xnom3d",
    "version": (1, 2, 0),
    "blender": (3, 0, 0),
    "location": "Graph/Dope Sheet & 3D View > Sidebar",
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}

import importlib

from . import properties
from .operators import (
    keyframe_offset,
    noise_randomizer,
    quick_flip,
    scene_cleanup,
    stagger_timing,
)
from .ui import panels

MODULES = (
    properties,
    noise_randomizer,
    keyframe_offset,
    stagger_timing,
    quick_flip,
    scene_cleanup,
    panels,
)


def register():
    for module in MODULES:
        importlib.reload(module)
    for module in MODULES:
        module.register()


def unregister():
    for module in reversed(MODULES):
        module.unregister()