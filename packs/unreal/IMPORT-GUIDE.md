# One-room house plan — living — Unreal import guide

#001 This pack is a derived artifact of a mojulo recipe (`recipe/sk_lkypzdim4y.json`); re-mint it from the recipe rather than hand-editing. Target editor: Unreal Engine 5 (5.4+; proven against UE 5.8.0).
#002 Steps marked T are editor actions, one per line, in order. Everything not listed here is done by the importer script — do not set values by hand that the importer already sets.

## ① Create the project

T001 Epic Games Launcher > Unreal Engine > Library > Launch(your installed 5.x) > Games > Third Person > Blueprint > Create
T001.01 any 5.4+ editor works; proven against UE 5.8.0
T001.02 macOS prerequisite: full Xcode must be installed and opened once (license accepted) — the editor cannot compile Metal shaders without it and any rendered run exits with "Xcode Not Found"
T001.03 macOS, Xcode 26+: also run `xcodebuild -downloadComponent MetalToolchain` (Xcode ships without the Metal compiler; the editor dialogs "missing Metal Toolchain" until it is downloaded)

## ② Enable Python

T002 Edit > Plugins > search `Python Editor Script Plugin` > Enabled > Restart Now
T002.01 while there, confirm `Interchange glTF`(glTF importer) shows Enabled — it is on by default in 5.3+

## ③ Copy the pack in

T003 Finder > copy this whole folder into the project root as `MojuloPack`, beside the `.uproject` (final path: `<Project>/MojuloPack`) — NOT into `Content/`; the importer writes the imported assets to `Content/MojuloPack` itself

## ④ Run the importer

T004 Window > Output Log > command bar dropdown(currently `Cmd`) > `Python` > run: `py MojuloPack/import_mojulo.py`
T004.01 Output Log — confirm one line: `[mojulo] level 'One-room house plan — living' -> /Game/MojuloPack/Maps/mojulo-level`

## ⑤ Open and play — the eyes gate

T005 Content Browser > Content > MojuloPack > Maps > `mojulo-level` — open
T006 Toolbar > [Play] — judge with your own eyes:
#003 the world mesh is LIT by MojuloSun + the sky atmosphere through M_MojuloLit — sun patches through the panes, a blue sky in the windows, no "Preview" stamp on the shadows (reference look: blender-bake.mjs --render)
#004 you can walk the level as the template character — the floor holds (the promoted ground plane) and the obstacle colliders block
#005 scale reads right at a 1.61544 m eye height — doors, steps, cover

## What travelled, what didn't

#101 sky_approximated — sky/backdrop dropped as mesh — approximate with the engine sky/fog
#102 skipped_runtime — game shell, AI, combat feel — re-orchestrate in-engine; reference performance is the web build
#103 lights_carried ×9 — recessed pot lights ride the GLB as KHR_lights_punctual spots (candela) and the score carries them too; Blender, Godot and Unity import them from the GLB (Godot converts candela to its lamp energy in the pack kernel), the Unreal importer spawns SpotLights from score.json when Interchange brings none
#104 textures_carried ×1 — surface/atlas textures travel inside the GLB (Interchange imports them as base-colour maps — pinned at the first machine gate); the web build is the reference look
#105 promoted_ground — implicit runtime ground plane promoted by the importer — the collider AABBs are obstacle hulls only, never the floor
#106 entity_markers — entities that baked no mesh (glyph/primitive bodies — export-side gap) get placeholder markers; the web build is the reference look
#107 cameras_data_only ×2 — authored camera framings ride score.json as data; the walker camera is the play view
