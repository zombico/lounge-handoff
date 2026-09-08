extends SceneTree
# Representation capture: two camera moves inside the lounge, saved as a PNG
# sequence. Frame-indexed, so the same script gives the same frames.
const FPS := 30
const OUT := "frames"   # run: godot --path packs/godot-lit --resolution 1280x720 --script ../../videos/godot-walkthrough.gd (mkdir frames first, relative to the pack)
var cam: Camera3D

func _init() -> void:
	var scene = load("res://level.tscn").instantiate()
	root.add_child(scene)
	for i in range(3):
		await process_frame
	cam = Camera3D.new()
	cam.fov = 62.0
	cam.near = 0.05
	root.add_child(cam)
	cam.current = true
	var n := 0
	# Move 1 — push in from the door toward the media wall, 5 s.
	var f1 := FPS * 5
	for i in range(f1):
		var t := ease(float(i) / float(f1 - 1), -1.8)
		cam.position = Vector3(3.66, 1.55, -7.25).lerp(Vector3(3.66, 1.35, -4.9), t)
		cam.look_at(Vector3(3.66, 1.0, -0.9))
		n = await _shot(n)
	# Move 2 — a slow eye-height orbit about the seating group, 9 s.
	var f2 := FPS * 9
	var centre := Vector3(3.66, 0.9, -3.4)
	for i in range(f2):
		var a := TAU * float(i) / float(f2) + PI * 0.5
		cam.position = centre + Vector3(cos(a) * 2.1, 0.75, sin(a) * 2.1)
		cam.look_at(centre)
		n = await _shot(n)
	print("[capture] frames=%d" % n)
	quit()

func _shot(n: int) -> int:
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("%s/frame_%04d.png" % [OUT, n])
	return n + 1
