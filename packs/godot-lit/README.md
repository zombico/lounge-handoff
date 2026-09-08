# One-room house plan — living — Godot handoff

A generated Godot 4 pack (mojulo `export-godot`). The world's truth lives
in `recipe/` — this whole folder is a derived artifact; re-mint it from the
recipe rather than hand-editing. The pack is DATA (`score.json`, the GLB,
audio) performed by the versioned mojulo-godot kernel in `kernel/`
(v0.2.1) — one score, two instruments; the web build is the
reference performance.

## Provenance

- source ref: `sk_lkypzdim4y`
- manifest sha256/16: `fc95e0c38dd696a1`
- kernel: mojulo-godot 0.2.1
- units: 1 mojulo unit = 1 meter; frame converted z-up → y-up by the kernel, matching the GLB root
- re-mint: `node scripts/export-godot.mjs --ref sk_lkypzdim4y` (from mojulo's `control/`)

## Open and play

Open the folder in Godot ≥4.5 (or `godot --path .`) and run. WASD/arrows to
walk, mouse to look, Space jumps, Esc frees the mouse, 0 toggles the authored camera framing.

## What travelled, what didn't

- `sky_approximated` — sky/backdrop dropped as mesh — approximate with the engine sky/fog
- `skipped_runtime` — game shell, AI, combat feel — re-orchestrate in-engine; reference performance is the web build
- `lights_carried` ×9 — recessed pot lights ride the GLB as KHR_lights_punctual spots (candela); Blender / Godot import them, the Unreal importer spawns SpotLights from score.json when Interchange brings none
- `textures_carried` ×1 (wood-oak) — surface/atlas textures travel inside the GLB and multiply with the baked vertex colours (kernel material fixup) — the web build is the reference look
- `entity_markers` — entities that baked no mesh (glyph/primitive bodies — export-side gap) render as gold placeholder markers; the web build is the reference look
- `web_color_shift` — web preset renders via GL Compatibility, which reads vertex colours as sRGB — linear COLOR_0 draws darker there; desktop uses Forward+ and is colour-true
- `promoted_ground` — implicit runtime ground plane promoted by the kernel — the collider AABBs are obstacle hulls only, never the floor
