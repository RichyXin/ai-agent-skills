# Figma MCP Usage (quick guide)

## When to use
Use when you have a Figma link/node-id and need precise layout/typography/color details or asset exports.

## Core steps
1. Parse the Figma URL for fileKey and node-id.
2. Call mcp__Framelink_Figma_MCP__get_figma_data with fileKey and nodeId.
3. Set depth to 4-6 to capture nested frames/components.
4. If icons/images are needed, call mcp__Framelink_Figma_MCP__download_figma_images for specific nodes.

## Tips
- Always scope to the exact node-id to avoid noisy data.
- If node-id is missing, ask the user to provide it.
- Confirm whether the design uses variants/components; if so, fetch the resolved instance node.
- For text styles, capture font family, size, line height, letter spacing, and weight.
- For colors, capture fills and strokes; map to semantic tokens in Android.
- For effects, capture radius, opacity, and shadow parameters.

## Example (pseudocode)
- get_figma_data(fileKey="...", nodeId="123:456", depth=5)
- download_figma_images(fileKey="...", nodes=[{nodeId:"789:101", fileName:"ic_nav.svg"}])
