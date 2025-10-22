# YABQOLA - Yet Another Blender Quality of Life Extension

**Version:** 1.2.1 - **Blender Compatibility:** 4.2+

YABQOLA is a modular collection of animation utilities for Blender created by **Xnom3d**. It focuses on speeding up common cleanup and timing tasks so you can stay in the flow while animating. Install it once and access every tool from the **Graph Editor**, **Dope Sheet**, or **3D Viewport** sidebars under the **YABQOLA** tab.

> Note: YABQOLA is actively evolving. We're committed to shipping new tools and refinements based on community suggestions; share your ideas and help guide the roadmap!

## Why Move to the Extensions Platform

- Blender 4.2 introduces the extensions framework for cleaner, future-proof distribution.
- Extension metadata lives in `blender_manifest.toml`, replacing `bl_info` for packaging.
- Dependencies can be bundled as Python wheels to ensure offline installs.
- Extensions must declare permissions up front so users know what data is accessed.
- Converting is mostly a packaging update, so your existing Python modules still work.

---

## Features at a Glance

- **Noise Randomizer**
  - Randomizes phase, offset, strength, and scale across noise modifiers.
  - Optional creation of missing noise modifiers.
  - Seeded randomness for reproducible variations.

- **Keyframe Offset**
  - Shift keyframes forward or backward by any number of frames.
  - Target only selected keys or entire F-Curves.
  - Cascade offsets by selection order or alphabetical channel names.

- **Stagger Timing**
  - Cascading offsets across multiple objects or pose bones to create natural overlap.
  - Works with shape keys and can run in reverse selection order.

- **Quick Flip**
  - Smart flip: mirrors poses on armatures and transforms on other objects in one click.
  - Dedicated pose-only and objects-only operators with configurable scope and axis.

- **Scene Cleanup**
  - Identifies and removes invisible or unused objects.
  - Dry-run preview before deletion, with safeguards for cameras, lights, and linked data.

- **Still Render Presets**
  - One-click Cycles and Eevee presets tuned for clay previews, draft stills, and final hero frames.
  - Keeps motion blur, sampling, and output formats in sync across render engines.

- **Reference Camera Matcher**
  - Syncs sensor size, focal length, and render resolution to match a reference image.
  - Supports crop-factor conversion, horizontal/vertical FOV targets, and optional camera background overlays.

---

## Installation

### Blender 4.2+ (Extensions)

1. Download the latest packaged `.zip` from the Releases page (or run `python scripts/package_addon.py --force` to build one).
2. In Blender, open **Edit > Preferences > Extensions**.
3. Click **Install from Disk**, pick the downloaded zip, and enable **YABQOLA**.
4. Restart Blender if prompted so the extension registers its keymaps.

### Blender 3.x Legacy Add-on (Optional)

Older Blender versions without the Extensions browser can still install YABQOLA as a traditional add-on:

1. Clone or copy this repository into your Blender add-ons folder:
   - Windows: `%APPDATA%/Blender Foundation/Blender/<version>/scripts/addons`
   - macOS: `~/Library/Application Support/Blender/<version>/scripts/addons`
   - Linux: `~/.config/blender/<version>/scripts/addons`
2. Restart Blender and enable the add-on from **Edit > Preferences > Add-ons** by searching for "YABQOLA".

---

## Getting Started

1. After enabling the add-on, open the **Graph Editor**, **Dope Sheet**, or **3D Viewport**.
2. Press `N` to reveal the sidebar and look for the **YABQOLA** tab.
3. Configure defaults in the sidebar panels; the settings persist per scene.

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
- Pick an **Offset Mode**: Uniform, Selection Order, or Name.
- Run **Apply Offset** to nudge timing as a batch operation.
- Great for quick re-timing without diving into individual curves.

### Stagger Timing

- Define the **Step** size to specify the frame delta between successive objects or pose bones.
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

### Still Render Presets

- Pick from clay, draft, or final still presets tuned for both Cycles and Eevee.
- Apply output, sampling, and motion blur overrides in one click via the sidebar or add-on preferences.

### Reference Camera Matcher

- Load a reference image to automatically align render resolution, sensor fit, and lens data.
- Choose from common camera presets or enter custom sensor dimensions.
- Match by 35mm-equivalent focal length or target horizontal/vertical FOV values.
- Optionally display the reference as a camera background for immediate framing feedback.

## Release Notes

### 1.2.1

- Added selection order and name-based cascade options to the Keyframe Offset tool.

## Roadmap & Feedback

YABQOLA will keep growing with your input. We're prioritizing:

- Additional animation utilities (e.g., curve normalization, ease presets).
- Quality-of-life improvements surfaced by everyday usage.
- Documentation and tutorial content.

Have a suggestion or workflow pain point? Open an issue or start a discussion-your ideas directly shape upcoming releases.

---

## Contributing

1. Fork the repository and create a feature branch.
2. Follow Blender's Python style (PEP 8) and keep modules self-contained.
3. Run the add-on locally to verify your changes.
4. Submit a pull request describing the motivation and testing performed.

Bug reports, UX feedback, and documentation updates are equally welcome.

---

## Automated Releases

This project includes a packaging helper and GitHub Actions workflow to publish extension zips automatically.

### Local packaging

- Run `python scripts/package_addon.py --force` to create `dist/xnom3d_yabqola-<version>.zip` using the manifest version.
- Use `--suffix` to append build metadata (for example `--suffix nightly`).

### GitHub Actions

- Pushing a tag that starts with `v` (for example `v1.2.1`) triggers the **Release** workflow, builds the zip, and publishes a GitHub Release with the artifact attached.
- You can also start the workflow manually from the Actions tab. Provide the release tag (e.g. `v1.2.1`) and optionally mark it as a draft or prerelease. The workflow will tag the commit you select and attach the packaged zip automatically.

Artifacts from any run are uploaded as workflow artifacts so they can be downloaded without publishing the release.

---

## Support & Issues

- File bugs and feature requests via the repository issue tracker.
- For quick questions, reach out on the project's Discord or preferred chat (if available).

---

## License

YABQOLA is distributed under the GPL-3.0-or-later license. Refer to `blender_manifest.toml` for authoritative metadata when submitting to the Extensions platform.

---

## Credits

- **Author:** Xnom3d
- **Contributors:** Add your name here via pull request!
