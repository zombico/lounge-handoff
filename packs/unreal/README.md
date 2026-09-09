# One-room house plan — living — Unreal handoff

A generated Unreal pack (mojulo `export-unreal`, leg v0.4.2). The world's truth
lives in `recipe/` — this whole folder is a derived artifact; re-mint it from
the recipe rather than hand-editing. The pack is DATA (`score.json`, the GLB)
realized by `import_mojulo.py` inside a stock Unreal Engine 5 (5.4+; proven against UE 5.8.0) Third Person
project — follow `IMPORT-GUIDE.md`; the web build is the reference performance.
The mechanics vocabulary is data-only in a world pack (the MojuloKernel plugin
ships with game packs).

## Provenance

- source ref: `sk_lkypzdim4y`
- manifest sha256/16: `fc95e0c38dd696a1`
- unreal leg: v0.4.2, target Unreal Engine 5 (5.4+; proven against UE 5.8.0), importer Interchange glTF
- units: 1 mojulo unit = 1 meter → UE centimeters (×100 in the importer); frame z-up → z-up left-handed, P(v) = (x·100, −y·100, z·100), gate-pinned, implemented in `import_mojulo.py` and `MojuloScore.cpp` (must stay identical)
- re-mint: `node scripts/export-unreal.mjs --ref sk_lkypzdim4y --lit` (from mojulo's `control/`)

## What travelled, what didn't

- `sky_approximated` — sky/backdrop dropped as mesh — approximate with the engine sky/fog
- `skipped_runtime` — game shell, AI, combat feel — re-orchestrate in-engine; reference performance is the web build
- `lights_carried` ×9 — recessed pot lights ride the GLB as KHR_lights_punctual spots (candela) and the score carries them too; Blender, Godot and Unity import them from the GLB (Godot converts candela to its lamp energy in the pack kernel), the Unreal importer spawns SpotLights from score.json when Interchange brings none
- `contract` — declares T0 (coherent); for T1 (baked): out_normals — 99.9% of faces carry outNormal (a bake reads winding from it)
- `textures_carried` ×1 (wood-oak) — surface/atlas textures travel inside the GLB (Interchange imports them as base-colour maps — pinned at the first machine gate); the web build is the reference look
- `promoted_ground` — implicit runtime ground plane promoted by the importer — the collider AABBs are obstacle hulls only, never the floor
- `entity_markers` — entities that baked no mesh (glyph/primitive bodies — export-side gap) get placeholder markers; the web build is the reference look
- `cameras_data_only` ×2 — authored camera framings ride score.json as data; the walker camera is the play view
