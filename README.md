# YABQOLA — Yet Another Blender Quality of Life Add-on

**Version:** 1.2.0 · **Blender Compatibility:** 3.0+

YABQOLA is a modular collection of animation utilities for Blender created by **Xnom3d**. It focuses on speeding up common cleanup and timing tasks so you can stay in the flow while animating. Install it once and access every tool from the **Graph Editor**, **Dope Sheet**, or **3D Viewport** sidebars under the **YABQOLA** tab.

> 💡 YABQOLA is actively evolving. We're committed to shipping new tools and refinements based on community suggestions—share your ideas and help guide the roadmap!

---

## Features at a Glance

- **Noise Randomizer**
  - Randomizes phase, offset, strength, and scale across noise modifiers.
  - Optional creation of missing noise modifiers.
  - Seeded randomness for reproducible variations.

- **Keyframe Offset**
  - Shift keyframes forward or backward by any number of frames.
  - Target only selected keys or entire F-Curves.

- **Stagger Timing**
  - Cascading offsets across multiple objects to create natural overlap.
  - Works with shape keys and can run in reverse selection order.

- **Quick Flip**
  - Smart flip: mirrors poses on armatures and transforms on other objects in one click.
  - Dedicated pose-only and objects-only operators with configurable scope and axis.

- **Scene Cleanup**
  - Identifies and removes invisible or unused objects.
  - Dry-run preview before deletion, with safeguards for cameras, lights, and linked data.

---

## Installation

### From a Release Zip

1. Download the latest `.zip` from the Releases page (or package this repository as a zip).
2. In Blender, open **Edit ▸ Preferences ▸ Add-ons**.
3. Click **Install**, pick the downloaded zip, enable **YABQOLA: Yet Another Blender Quality of Life Add-on**.

### From Source (Developer Setup)

1. Clone the repository into your Blender add-ons folder:
   - Windows: `%APPDATA%/Blender Foundation/Blender/<version>/scripts/addons`
   - macOS: `~/Library/Application Support/Blender/<version>/scripts/addons`
   - Linux: `~/.config/blender/<version>/scripts/addons`
2. Restart Blender and enable the add-on from **Preferences ▸ Add-ons**.

---

## Getting Started

1. After enabling the add-on, open the **Graph Editor**, **Dope Sheet**, or **3D Viewport**.
2. Press `N` to reveal the sidebar and look for the **YABQOLA** tab.
3. Configure defaults in the sidebar panels—the settings persist per scene.

Each feature lives in its own collapsible panel so you can focus on the tools you use most. Hover over any control to see contextual tooltips.

---

## Tool Guide

### Noise Randomizer

- Set minimum and maximum values for phase, offset, strength, and scale.
- Toggle **Create Missing** to add noise modifiers automatically when absent.
- Use **Only Selected Curves** to limit the operation to highlighted F-Curves.
- Hit **Randomize Noise** to apply the changes.

### Keyframe Offset

- Choose a **Frame Offset** and whether to affect only selected keys.
- Run **Apply Offset** to nudge timing as a batch operation.
- Great for quick re-timing without diving into individual curves.

### Stagger Timing

- Define the **Step** size to specify the frame delta between successive objects.
- Enable **Reverse Order** to invert the staggering direction.
- Include shape keys when animating facial rigs or morph targets.
- Use **Stagger** to distribute the offsets automatically.

### Quick Flip

- Pick your scope: **Selection** or an entire **Collection** (with optional sub-collections and child objects).
- Choose the axis to mirror against.
- Execute one of three operators:
  - **Smart Flip** for mixed armature/object selections.
  - **Flip Pose** to paste flipped armature poses only.
  - **Flip Objects** to mirror non-armature transforms.

### Scene Cleanup

- Decide whether viewport/render visibility should count as "visible".
- Protect lights, cameras, and linked data with the provided toggles.
- Use **Preview** (dry run) to review candidates, then **Delete** to clean.

---

## Roadmap & Feedback

YABQOLA will keep growing with your input. We're prioritizing:

- Additional animation utilities (e.g., curve normalization, ease presets).
- Quality-of-life improvements surfaced by everyday usage.
- Documentation and tutorial content.

Have a suggestion or workflow pain point? Open an issue or start a discussion—your ideas directly shape upcoming releases.

---

## Contributing

1. Fork the repository and create a feature branch.
2. Follow Blender's Python style (PEP 8) and keep modules self-contained.
3. Run the add-on locally to verify your changes.
4. Submit a pull request describing the motivation and testing performed.

Bug reports, UX feedback, and documentation updates are equally welcome.

---

## Support & Issues

- File bugs and feature requests via the repository issue tracker.
- For quick questions, reach out on the project's Discord or preferred chat (if available).

---

## License

No explicit license has been provided yet; all rights reserved by the author. If you plan to distribute modified versions, please coordinate with the maintainer.

---

## Credits

- **Author:** Xnom3d
- **Contributors:** Add your name here via pull request!
