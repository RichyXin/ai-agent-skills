---
name: figma-android-ui-restore
description: High-fidelity Figma-to-Android UI restoration for XML or Compose. Use when given a Figma link/node and a target Android module/file and you must match layout, typography, colors, states, custom views, and day/night theming with minimal drift.
---

# Figma Android UI Restore

## Overview
Produce strict, pixel-faithful Android UI implementations from Figma by extracting node specs, mapping tokens to resources, handling custom views and parent-child effects, and validating day/night themes.

## Workflow (use in order)
1. Collect inputs: Figma link + node-id, target file path(s), UI tech (XML/Compose), target module, day/night requirement, custom view list, and existing style/color/dimens conventions.
2. Load Figma structure: use references/figma-mcp.md to fetch nodes and assets; scope to the exact node-id; keep depth 4-6 unless a component is deeply nested.
3. Translate layout: map auto-layout to Linear/Constraint, absolute to Frame/Constraint; preserve spacing, padding, alignment, fixed sizes, and text baselines.
4. Map tokens to Android resources: create or reuse colors, dimens, and text appearances; avoid hardcoded values in layout unless explicitly required.
5. Apply module-specific dimens rules: use references/dimens-mapping.md to select mon_xx/mon_sp_xx or common_xxdp/common_xxsp and avoid direct Figma values.
6. Handle custom views and parent-child interactions: read custom view code to confirm default padding/size, styleable attrs, and internal layout; check for parent constraints, clipping, and weight/bias side effects.
7. Implement: update XML/Compose, add resources, update theme overlays and night resources; ensure states (pressed/disabled/selected) match Figma.
8. Run on device via adb: launch the exact target page/activity/fragment path with adb commands (or app deep link) and ensure the final rendered screen is visible.
9. Capture screenshot via adb: save screenshots locally with versioned names after each implementation pass.
10. Compare and iterate: self-compare adb screenshots against Figma node (layout, spacing, typography, colors, radius, icon scale, state visuals). If any mismatch remains, revise code and repeat steps 8-10 until visually aligned.
11. Verify completion: only stop when no visible mismatch remains in required states (at least default state; include pressed/disabled/selected/night if required by task).

## Fidelity rules (must follow)
- No approximation: use exact dp/sp values derived from Figma measurements.
- Preserve typography: font family, weight, size, letter spacing, and line height.
- Colors must map to semantic tokens and support day/night via resource qualifiers.
- Match shape details: corner radius, stroke, elevation/shadow; emulate if direct mapping is missing.
- Respect parent-child effects: padding, clipping, constraints, and chain/bias behavior.
- For custom views, prefer styleable attrs and reusable styles over magic numbers.
- Use module-specific dimens resources only (Monterey: mon_xx/mon_sp_xx; Cardiff: common_xxdp/common_xxsp).
- If Figma matches a design system component, use the component and tune tokens instead of recreating.
- Device validation is mandatory: do not claim completion without adb page navigation + adb screenshot evidence.
- Iterative correction is mandatory: if screenshot-vs-Figma diff exists, continue editing and re-capturing until resolved.

## Common pitfalls (avoid)
- Material defaults overriding text/shape styles.
- ConstraintLayout chains or bias altering intended spacing.
- Night theme reusing day colors.
- wrap_content where Figma specifies fixed size.
- Ignoring image/icon scaling mode (fit vs centerCrop).

## ADB verification loop (mandatory)
- Use reproducible adb commands and record them in output.
- Recommended command sequence per iteration:
  1. `adb devices` to ensure target device is online.
  2. Navigate to target page with explicit command (example: `adb shell am start -n <package>/<activity>` or `adb shell am start -a android.intent.action.VIEW -d "<deeplink>"`).
  3. Wait for stable rendering (`adb shell sleep 1` or equivalent).
  4. Capture screenshot (example: `adb exec-out screencap -p > /tmp/ui_restore_iter_01.png`).
  5. Compare with Figma and list mismatches by category (layout/spacing/typography/color/shape/state/icon scale).
  6. Apply fixes and run the next iteration with incremented screenshot name.
- If adb navigation or screenshot cannot be completed, mark task as blocked and provide exact failing command + stderr.

## Output expectations
- Provide a patch/diff or list changed files with rationale.
- Include adb execution evidence: page navigation command(s), screenshot path(s), and each iteration's mismatch/fix notes.
- Explicitly state convergence result: either "matched" or "remaining mismatch + reason blocked".
- Call out assumptions, missing assets, or unresolved design tokens.

## Resources
- references/figma-mcp.md: Extract Figma nodes/assets via MCP.
- references/android-restore-checklist.md: Detailed fidelity checklist.
- references/dimens-mapping.md: Monterey/Cardiff dimens rules and examples.
