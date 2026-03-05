# Android UI Fidelity Checklist

## Layout
- [ ] Container type matches (Frame/Linear/Constraint/Relative/Compose layout).
- [ ] Fixed sizes respected; no unintended wrap_content.
- [ ] Padding/margin match Figma in dp.
- [ ] Alignment and gravity match (start/center/end, baseline).
- [ ] Constraints, chains, and bias reflect Figma positioning.
- [ ] Parent clipping/overlap matches (clipToPadding/clipChildren).

## Typography
- [ ] Font family and weight match.
- [ ] Font size and line height match.
- [ ] Letter spacing matches.
- [ ] Text color matches and is tokenized.

## Color and Shape
- [ ] Fill colors map to semantic resources.
- [ ] Stroke width/color match.
- [ ] Corner radius match.
- [ ] Elevation/shadow match (or emulated).

## Components and States
- [ ] Component variants match (default/pressed/selected/disabled).
- [ ] Icons/images use correct scale and tint.
- [ ] Custom view attributes applied via styleable attrs.

## Day/Night
- [ ] Colors have day and night variants.
- [ ] Theme overlay is applied correctly.
- [ ] Contrast preserved in night mode.

## Asset Integrity
- [ ] Icons/images exported at correct size and format (SVG/PNG).
- [ ] Vector drawables preserve stroke width and viewport.

## Regression Risks
- [ ] No conflicts with existing styles/themes.
- [ ] No unintended layout changes in other screens.
