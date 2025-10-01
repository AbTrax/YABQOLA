"""
Animation QoL Add-on Package
"""

bl_info = {
    "name": "Animation QoL Toolkit",
    "description": "Modular tools to streamline animation workflows with noise randomization and timing utilities.",
    "author": "Xnom3d",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Graph Editor > Sidebar",
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}

import importlib

from . import properties
from .operators import keyframe_offset, noise_randomizer, stagger_timing
from .ui import panels

MODULES = (
    properties,
    noise_randomizer,
    keyframe_offset,
    stagger_timing,
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