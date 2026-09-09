"""Representation capture, Unreal leg: builds two Level Sequences in the scratch
project mojulo's export-unreal gate wrote, frame-indexed so a re-run gives the same
frames. Run under the editor Python commandlet (no RHI needed to author):

  UnrealEditor-Cmd <scratch>/Mojulo.uproject -run=pythonscript -script=videos/unreal-cine.py -unattended -nullrhi -nosplash

then render each sequence with the stock Render-Movie capture, headless in -game:

  UnrealEditor <scratch>/Mojulo.uproject /Game/MojuloPack/Maps/mojulo-level -game -windowed -ResX=1280 -ResY=720 -ForceRes \
    -MovieSceneCaptureType="/Script/MovieSceneCapture.AutomatedLevelSequenceCapture" \
    -LevelSequence="/Game/MojuloPack/Cine/LS_Walkthrough" -MovieFolder=<frames dir> -MovieName="walkthrough.{frame}" \
    -MovieFormat=PNG -MovieFrameRate=30 -MovieQuality=100 -MovieWarmUpFrames=60 -MovieCinematicMode=Yes -NoLoadingScreen -NoScreenMessages \\
    -ExecCmds="r.MotionBlurQuality 0"   # no motion blur: the Godot capture has none, and the orbit smears at 30 fps otherwise

Shots are authored in mojulo's own frame (metres, z-up) and mapped with the leg's
pinned P(v) = (x*100, -y*100, z*100), the same map import_mojulo.py uses, so the
camera path is the Godot walkthrough's path, not a re-authoring of it.
"""
import math
import unreal

MAP = '/Game/MojuloPack/Maps/mojulo-level'
CINE = '/Game/MojuloPack/Cine'
FPS = 30
FOCAL_MM = 16.0   # 16 mm on the 16:9 digital-film back: ~73 deg horizontal, a room lens


def P(v):
    return unreal.Vector(v[0] * 100.0, -v[1] * 100.0, v[2] * 100.0)


def aim(cam, target):
    """UE pitch/yaw (degrees) that points cam at target."""
    dx, dy, dz = target.x - cam.x, target.y - cam.y, target.z - cam.z
    return math.degrees(math.atan2(dz, math.hypot(dx, dy))), math.degrees(math.atan2(dy, dx))


def smooth(t):
    return t * t * (3.0 - 2.0 * t)


def unwrap(prev, yaw):
    if prev is None:
        return yaw
    while yaw - prev > 180.0:
        yaw -= 360.0
    while yaw - prev < -180.0:
        yaw += 360.0
    return yaw


def new_sequence(name, frames):
    path = CINE + '/' + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    unreal.EditorAssetLibrary.make_directory(CINE)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    seq = tools.create_asset(name, CINE, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    seq.set_display_rate(unreal.FrameRate(FPS, 1))
    seq.set_playback_start(0)
    seq.set_playback_end(frames)
    return seq, path


def _lens(comp, focal=FOCAL_MM):
    comp.set_editor_property('current_focal_length', focal)
    try:
        focus = comp.get_editor_property('focus_settings')
        focus.set_editor_property('focus_method', unreal.CameraFocusMethod.DISABLE)
        comp.set_editor_property('focus_settings', focus)
    except Exception as e:  # depth of field is cosmetic here
        unreal.log_warning('[mojulo-cine] focus settings: ' + str(e))


def spawn_camera(seq, focal=FOCAL_MM):
    """A spawnable CineCameraActor owned by the sequence when its template exposes
    the lens; otherwise one level-placed CineCameraActor 'MojuloCineCamera' that
    every sequence possesses (reused across runs, saved with the map)."""
    binding = seq.add_spawnable_from_class(unreal.CineCameraActor)
    binding.set_name('MojuloCineCamera')
    tmpl = binding.get_object_template()
    comp = None
    for get in (lambda: tmpl.get_cine_camera_component(),
                lambda: tmpl.get_editor_property('cine_camera_component'),
                lambda: tmpl.get_editor_property('camera_component')):
        try:
            comp = get()
        except Exception:
            comp = None
        if comp is not None:
            break
    if comp is not None:
        _lens(comp, focal)
        return binding
    binding.remove()
    unreal.log_warning('[mojulo-cine] spawnable template exposes no camera component; possessing a level camera instead')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    cam = None
    for a in actors.get_all_level_actors():
        if isinstance(a, unreal.CineCameraActor) and a.get_actor_label() == 'MojuloCineCamera':
            cam = a
            break
    if cam is None:
        cam = actors.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(0, 0, 150), unreal.Rotator(0, 0, 0))
        cam.set_actor_label('MojuloCineCamera')
        _lens(cam.get_cine_camera_component(), focal)
        unreal.EditorLoadingAndSavingUtils.save_current_level()
    return seq.add_possessable(cam)


def transform_channels(binding, frames):
    track = binding.add_track(unreal.MovieScene3DTransformTrack)
    section = track.add_section()
    section.set_range(0, frames)
    chans = section.get_all_channels()   # Location XYZ, Rotation XYZ (roll, pitch, yaw), Scale XYZ
    if len(chans) < 9:
        raise RuntimeError('transform section has %d channels, expected 9' % len(chans))
    return chans


LIN = unreal.MovieSceneKeyInterpolation.LINEAR


def key(chan, f, value):
    chan.add_key(unreal.FrameNumber(f), float(value), 0.0, unreal.MovieSceneTimeUnit.DISPLAY_RATE, LIN)


def key_pose(chans, f, loc, pitch, yaw, roll=0.0):
    key(chans[0], f, loc.x); key(chans[1], f, loc.y); key(chans[2], f, loc.z)
    key(chans[3], f, roll);  key(chans[4], f, pitch); key(chans[5], f, yaw)
    if f == 0:
        for c in chans[6:9]:
            key(c, 0, 1.0)


def camera_cut(seq, binding, frames):
    cut = seq.add_track(unreal.MovieSceneCameraCutTrack)
    sec = cut.add_section()
    sec.set_range(0, frames)
    sec.set_camera_binding_id(seq.get_binding_id(binding))


# --- shot 1: the Godot walkthrough's two moves, same numbers -----------------
# Godot (x, y, z) y-up -> mojulo (x, -z, y) z-up. Move 1 pushes in from the door
# toward the media wall over 5 s; move 2 is a 9 s eye-height orbit of the seating group.
def build_walkthrough():
    f1, f2 = FPS * 5, FPS * 9
    frames = f1 + f2
    seq, path = new_sequence('LS_Walkthrough', frames)
    cam = spawn_camera(seq)
    ch = transform_channels(cam, frames)
    prev = None
    a0, a1 = P([3.66, 7.25, 1.55]), P([3.66, 4.90, 1.35])
    look1 = P([3.66, 0.90, 1.00])
    for i in range(f1):
        t = smooth(i / float(f1 - 1))
        loc = unreal.Vector(a0.x + (a1.x - a0.x) * t, a0.y + (a1.y - a0.y) * t, a0.z + (a1.z - a0.z) * t)
        pitch, yaw = aim(loc, look1)
        yaw = unwrap(prev, yaw); prev = yaw
        key_pose(ch, i, loc, pitch, yaw)
    cx, cy, cz = 3.66, 3.40, 0.90
    centre = P([cx, cy, cz])
    for i in range(f2):
        a = math.tau * i / float(f2) + math.pi * 0.5
        loc = P([cx + math.cos(a) * 2.1, cy - math.sin(a) * 2.1, cz + 0.75])
        pitch, yaw = aim(loc, centre)
        yaw = unwrap(prev, yaw); prev = yaw
        key_pose(ch, f1 + i, loc, pitch, yaw)
    camera_cut(seq, cam, frames)
    unreal.EditorAssetLibrary.save_asset(path)
    unreal.log('[mojulo-cine] %s: %d frames at %d fps' % (path, frames, FPS))
    return path, frames


# --- shot 2: day to night, an Unreal-only representation ---------------------
# Fixed camera at the media wall looking over the seating group at the south
# door wall. MojuloSun (the importer's own directional light, bound to the sky
# atmosphere) falls from mid-afternoon through the horizon over 10 s; the sky
# light follows the atmosphere down and the nine pot lights, 400 cd each in the
# glTF, are what is left. Lumen re-lights the room every frame; the pack does
# not change. The end frame is the Cycles night frame's Unreal twin. Unreal's
# auto-exposure would hold the room at daytime brightness all the way down, so an
# unbound post-process volume rides the sequence with its exposure bias keyed
# 0 -> -2.5 EV, the same lever mojulo's own night preset pulls (-2 EV): the camera
# operator's exposure, disclosed here, not a change to the pack or the lights.
def build_day_to_night():
    frames = FPS * 10
    seq, path = new_sequence('LS_DayToNight', frames)
    cam = spawn_camera(seq)
    ch = transform_channels(cam, frames)
    loc = P([3.66, 1.20, 1.40])
    pitch, yaw = aim(loc, P([3.66, 6.50, 1.70]))
    key_pose(ch, 0, loc, pitch, yaw)
    key_pose(ch, frames - 1, loc, pitch, yaw)
    camera_cut(seq, cam, frames)

    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    sun = None
    for a in actors:
        if isinstance(a, unreal.DirectionalLight) and a.get_actor_label() == 'MojuloSun':
            sun = a
            break
    if sun is None:
        raise RuntimeError('MojuloSun not found in ' + MAP)
    sb = seq.add_possessable(sun)
    sch = transform_channels(sb, frames)
    base = sun.get_actor_location()
    # UE pitch -45 = mid-afternoon; +12 = below the horizon. Yaw drifts west.
    for i in range(frames):
        t = i / float(frames - 1)
        e = smooth(t)
        pitch = -45.0 + 57.0 * e
        yaw = 40.0 - 60.0 * e
        key_pose(sch, i, base, pitch, yaw)

    post = None
    for a in actors:
        if isinstance(a, unreal.PostProcessVolume) and a.get_actor_label() == 'MojuloCinePost':
            post = a
            break
    if post is None:
        sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        post = sub.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
        post.set_actor_label('MojuloCinePost')
        post.set_editor_property('unbound', True)
        pps = post.get_editor_property('settings')
        pps.set_editor_property('override_auto_exposure_bias', True)
        pps.set_editor_property('auto_exposure_bias', 0.0)
        post.set_editor_property('settings', pps)
        unreal.EditorLoadingAndSavingUtils.save_current_level()
    pb = seq.add_possessable(post)
    ev = pb.add_track(unreal.MovieSceneFloatTrack)
    ev.set_property_name_and_path('AutoExposureBias', 'Settings.AutoExposureBias')
    evs = ev.add_section()
    evs.set_range(0, frames)
    evc = evs.get_all_channels()[0]
    for i in range(frames):
        key(evc, i, -2.5 * smooth(i / float(frames - 1)))
    unreal.EditorAssetLibrary.save_asset(path)
    unreal.log('[mojulo-cine] %s: %d frames at %d fps, sun keyed on %s, exposure bias 0 -> -2.5 EV' % (path, frames, FPS, sun.get_actor_label()))
    return path, frames


# --- still: the engine's frame from the walker's spawn ------------------------
# The eyes-gate incantation's camera (BugItGo at the door, the player camera's
# 90-degree horizontal field) as a 30-frame sequence, so the still gets the
# capture's warm-up and streamed-in textures; frame 29 is the picture.
def build_spawn_still():
    frames = 30
    seq, path = new_sequence('LS_Spawn', frames)
    cam = spawn_camera(seq, 11.88)   # 90 degrees across the 23.76 mm back, the player camera's field
    ch = transform_channels(cam, frames)
    loc = P([3.66, 7.25, 1.55])
    key_pose(ch, 0, loc, 0.0, 90.0)
    key_pose(ch, frames - 1, loc, 0.0, 90.0)
    camera_cut(seq, cam, frames)
    unreal.EditorAssetLibrary.save_asset(path)
    unreal.log('[mojulo-cine] %s: %d frames (a still)' % (path, frames))
    return path, frames


if __name__ == '__main__' or True:
    unreal.EditorLoadingAndSavingUtils.load_map(MAP)
    a = build_walkthrough()
    b = build_day_to_night()
    c = build_spawn_still()
    unreal.log('[mojulo-cine] done: %s, %s, %s' % (a, b, c))
