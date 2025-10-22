"""Property definitions for the YABQOLA add-on."""

from __future__ import annotations

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup, Scene

from .utils import SENSOR_PRESETS


def _refcam_on_preset_change(self, _context):
    preset = self.refcam_sensor_preset
    if preset == "CUSTOM":
        return
    sensor_width, sensor_height, _ = SENSOR_PRESETS[preset]
    self.refcam_sensor_width = sensor_width
    self.refcam_sensor_height = sensor_height


def _refcam_enable_equiv(self, _context):
    if self.refcam_use_equiv_35:
        self.refcam_use_fov_h = False
        self.refcam_use_fov_v = False


def _refcam_enable_fov_h(self, _context):
    if self.refcam_use_fov_h:
        self.refcam_use_equiv_35 = False
        self.refcam_use_fov_v = False


def _refcam_enable_fov_v(self, _context):
    if self.refcam_use_fov_v:
        self.refcam_use_equiv_35 = False
        self.refcam_use_fov_h = False


class AnimationQOLSceneSettings(PropertyGroup):
    """Persistent settings exposed in the UI panels."""

    # Noise randomizer configuration
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

    # Keyframe offset configuration
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

    keyframe_offset_mode: EnumProperty(
        name="Offset Mode",
        description="Choose how offsets are distributed across the targeted curves",
        items=(
            ("UNIFORM", "Uniform", "Shift every targeted keyframe by the same amount"),
            ("ORDER", "Selection Order", "Offset incrementally following the current curve order"),
            ("NAME", "Name", "Offset incrementally based on curve names"),
        ),
        default="UNIFORM",
    )

    # Stagger timing configuration
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

    # Ease preset configuration
    ease_preset: EnumProperty(
        name="Preset",
        description="Interpolation/handle preset to apply to targeted keyframes",
        items=(
            ("EASE_IN", "Ease In", "Ease into the motion by slowing at the beginning"),
            ("EASE_OUT", "Ease Out", "Ease out of the motion by slowing at the end"),
            ("EASE_IN_OUT", "Ease In-Out", "Ease at both the beginning and end"),
            ("LINEAR", "Linear", "Straight interpolation between keys"),
            ("CONSTANT", "Constant", "Hold the value until the next keyframe"),
        ),
        default="EASE_IN_OUT",
    )
    ease_only_selected_curves: BoolProperty(
        name="Only Selected Curves",
        description="Limit easing operations to explicitly selected curves",
        default=True,
    )
    ease_only_selected_keys: BoolProperty(
        name="Only Selected Keys",
        description="Only affect selected keyframes when applying the preset",
        default=True,
    )
    ease_include_shape_keys: BoolProperty(
        name="Include Shape Key Curves",
        description="Also affect shape key animations when gathering curves",
        default=True,
    )
    ease_affect_handles: BoolProperty(
        name="Adjust Handles",
        description="Update bezier handles alongside interpolation mode when applicable",
        default=True,
    )

    # Motion hold configuration
    hold_frame_count: IntProperty(
        name="Hold Length",
        description="Number of frames between the duplicated keys",
        default=6,
        min=1,
        soft_max=120,
        step=1,
    )
    hold_only_selected_curves: BoolProperty(
        name="Only Selected Curves",
        description="Only duplicate keys on selected curves",
        default=True,
    )
    hold_only_selected_keys: BoolProperty(
        name="Only Selected Keys",
        description="Only duplicate keys that are explicitly selected",
        default=True,
    )
    hold_include_shape_keys: BoolProperty(
        name="Include Shape Key Curves",
        description="Also process shape key animation curves",
        default=True,
    )
    hold_interpolation: EnumProperty(
        name="Hold Interpolation",
        description="Interpolation mode used for the duplicated hold keys",
        items=(
            ("CONSTANT", "Constant", "Maintain a stepped hold between keys"),
            ("LINEAR", "Linear", "Create a linear transition across the hold"),
            ("BEZIER", "Bezier", "Use bezier interpolation for the hold"),
        ),
        default="CONSTANT",
    )
    hold_inherit_handles: BoolProperty(
        name="Inherit Handles",
        description="Attempt to preserve outgoing handle shape when duplicating bezier keys",
        default=True,
    )

    # Render preset configuration
    render_preset: EnumProperty(
        name="Render Preset",
        description="Quick toggle for commonly used render configurations",
        items=(
            ("PREVIEW", "Preview", "Low-cost preview settings"),
            ("PLAYBLAST", "Playblast", "Balanced viewport capture settings"),
            ("STILL_DRAFT", "Still Draft", "Medium-quality still render with quick turnaround"),
            ("STILL_FINAL", "Still Final", "High-quality still render settings"),
            ("STILL_CLAY", "Still Clay", "Simplified clay render for lighting checks"),
            ("FINAL", "Final", "Legacy high-quality animation render settings"),
        ),
        default="PREVIEW",
    )
    render_adjust_output: BoolProperty(
        name="Adjust Output Settings",
        description="Update resolution, file format, and motion blur according to the preset",
        default=True,
    )
    render_adjust_samples: BoolProperty(
        name="Adjust Samples",
        description="Update render engine sample counts according to the preset",
        default=True,
    )
    # Quick flip configuration
    flip_scope: EnumProperty(
        name="Scope",
        description="Choose which objects are targeted for flip operations",
        items=(
            ("SELECTION", "Selection", "Use currently selected objects"),
            ("COLLECTION", "Collection", "Use objects from a collection"),
        ),
        default="SELECTION",
    )
    flip_collection: PointerProperty(
        name="Collection",
        description="Collection whose contents will be affected when scope is Collection",
        type=bpy.types.Collection,
    )
    flip_include_subcollections: BoolProperty(
        name="Include Sub-collections",
        description="Also include objects from child collections",
        default=True,
    )
    flip_include_children: BoolProperty(
        name="Include Hierarchy",
        description="Include hierarchy children of targeted objects",
        default=False,
    )
    flip_axis: EnumProperty(
        name="Axis",
        description="Axis used when mirroring object scale",
        items=(
            ("X", "X", "Mirror across the X axis"),
            ("Y", "Y", "Mirror across the Y axis"),
            ("Z", "Z", "Mirror across the Z axis"),
        ),
        default="X",
    )

    # Scene cleanup configuration
    cleanup_consider_viewport: BoolProperty(
        name="Consider Viewport Visibility",
        description="Treat objects hidden from the viewport as invisible",
        default=True,
    )
    cleanup_consider_render: BoolProperty(
        name="Consider Render Visibility",
        description="Treat objects disabled for rendering as invisible",
        default=True,
    )
    cleanup_keep_lights: BoolProperty(
        name="Keep Lights",
        description="Never remove lights or light probes",
        default=True,
    )
    cleanup_keep_cameras: BoolProperty(
        name="Keep Cameras",
        description="Never remove camera objects",
        default=True,
    )
    cleanup_keep_active_camera: BoolProperty(
        name="Always Keep Active Camera",
        description="Ensure the scene's active camera is preserved even if cameras are deletable",
        default=True,
    )
    cleanup_exclude_linked_data: BoolProperty(
        name="Skip Linked Data",
        description="Ignore objects that come from external libraries",
        default=True,
    )

    # Reference camera configuration
    refcam_image_path: StringProperty(
        name="Reference Image",
        subtype="FILE_PATH",
        description="File path to the reference image used for camera matching",
    )
    refcam_image: PointerProperty(
        name="Image Datablock",
        description="Loaded image datablock",
        type=bpy.types.Image,
    )
    refcam_sensor_preset: EnumProperty(
        name="Sensor Preset",
        description="Choose a sensor preset or switch to Custom to enter values manually",
        items=[
            ("FULL_FRAME", "Full Frame 36x24", SENSOR_PRESETS["FULL_FRAME"][2]),
            ("APS_C", "APS-C 23.6x15.7", SENSOR_PRESETS["APS_C"][2]),
            ("MFT", "Micro Four Thirds 17.3x13", SENSOR_PRESETS["MFT"][2]),
            ("SUPER35", "Super35 (Arri)", SENSOR_PRESETS["SUPER35"][2]),
            ("1_INCH", '1" type 13.2x8.8', SENSOR_PRESETS["1_INCH"][2]),
            ("IPHONE12_MAIN", "Phone Main (~1/1.76\")", SENSOR_PRESETS["IPHONE12_MAIN"][2]),
            ("CUSTOM", "Custom...", "Manually set sensor width and height"),
        ],
        default="FULL_FRAME",
        update=_refcam_on_preset_change,
    )
    refcam_sensor_width: FloatProperty(
        name="Sensor Width (mm)",
        default=SENSOR_PRESETS["FULL_FRAME"][0],
        min=0.1,
        soft_max=60.0,
    )
    refcam_sensor_height: FloatProperty(
        name="Sensor Height (mm)",
        default=SENSOR_PRESETS["FULL_FRAME"][1],
        min=0.1,
        soft_max=40.0,
    )
    refcam_override_fit: BoolProperty(
        name="Override Sensor Fit",
        description="If disabled, the sensor fit is chosen automatically based on image aspect ratio",
        default=False,
    )
    refcam_sensor_fit: EnumProperty(
        name="Sensor Fit",
        items=(("HORIZONTAL", "Horizontal", ""), ("VERTICAL", "Vertical", "")),
        default="HORIZONTAL",
    )
    refcam_use_equiv_35: BoolProperty(
        name="Use 35mm-Equivalent Focal",
        description="Calculate focal length from a 35mm equivalent value using diagonal crop factor",
        default=True,
        update=_refcam_enable_equiv,
    )
    refcam_equiv_35_mm: FloatProperty(
        name="35mm-Equivalent (mm)",
        default=50.0,
        min=1.0,
        soft_max=300.0,
    )
    refcam_use_fov_h: BoolProperty(
        name="Use Horizontal FOV",
        description="If enabled, compute the lens from the horizontal field of view",
        default=False,
        update=_refcam_enable_fov_h,
    )
    refcam_fov_h_deg: FloatProperty(
        name="FOV Horizontal (°)",
        default=60.0,
        min=1.0,
        max=179.0,
    )
    refcam_use_fov_v: BoolProperty(
        name="Use Vertical FOV",
        description="If enabled, compute the lens from the vertical field of view",
        default=False,
        update=_refcam_enable_fov_v,
    )
    refcam_fov_v_deg: FloatProperty(
        name="FOV Vertical (°)",
        default=45.0,
        min=1.0,
        max=179.0,
    )
    refcam_direct_lens_mm: FloatProperty(
        name="Direct Lens (mm)",
        description="Fallback focal length used when no computation option is enabled",
        default=35.0,
        min=1.0,
        soft_max=300.0,
    )
    refcam_add_background: BoolProperty(
        name="Show Reference in Camera View",
        description="Display the reference image as a background image in the active camera",
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
