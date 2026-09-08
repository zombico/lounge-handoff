# One-room house plan — living — Unity handoff

A generated Unity pack (mojulo `export-unity`, leg v0.4.0). The world's truth
lives in `recipe/` — this whole folder is a derived artifact; re-mint it from
the recipe rather than hand-editing. The pack is DATA (`score.json`, the GLB)
performed by the mojulo-unity kernel (`Editor/` builds the scene, `Runtime/`
performs the walker + mechanics live) inside a stock Unity 6 (6000.2.x) project —
follow `IMPORT-GUIDE.md`; the web build is the reference performance.

## Provenance

- source ref: `sk_lkypzdim4y`
- manifest sha256/16: `fee2b9a2a50a2857`
- unity leg: v0.4.0, target Unity 6 (6000.2.x), glTF importer `com.unity.cloud.gltfast`
- units: 1 mojulo unit = 1 meter; frame z-up → y-up baked into the GLB root, sidecar mapped by the kernel (one function, gate-asserted)
- re-mint: `node scripts/export-unity.mjs --ref sk_lkypzdim4y` (from mojulo's `control/`)

## What travelled, what didn't

- `sky_approximated` — sky/backdrop dropped as mesh — approximate with the engine sky/fog
- `skipped_runtime` — game shell, AI, combat feel — re-orchestrate in-engine; reference performance is the web build
- `lights_carried` ×9 — recessed pot lights ride the GLB as KHR_lights_punctual spots (candela); Blender / Godot import them, the Unreal importer spawns SpotLights from score.json when Interchange brings none
- `textures_carried` ×1 (wood-oak) — surface/atlas textures travel inside the GLB (glTFast imports them as albedo maps) — the web build is the reference look
- `promoted_ground` — implicit runtime ground plane promoted by the importer — the collider AABBs are obstacle hulls only, never the floor
- `entity_markers` — entities that baked no mesh (glyph/primitive bodies — export-side gap) render as gold placeholder markers; the web build is the reference look
- `cameras_data_only` ×2 — authored camera framings ride score.json as data; the walker head camera is the play view
