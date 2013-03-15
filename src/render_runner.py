""" Controls Blender rendering."""
import argparse
import bpy
import inspect
import os
import sys
#
from pdb import set_trace as BP


class DeviceError(Exception):
    pass


gpu_devices = ("CUDA", "OPENCL")


def run(device_t=None, scenes=False, samples=None):
    """ Run rendering procedures."""

    def render(scene, device, samples):
        """ Set the scene and do the render."""
        # Make scene active.
        bpy.context.screen.scene = scene
        # Set the rendering device.
        scene.cycles.device = device
        # Print device setting.
        print(scene.cycles.device)
        # Set number of samples.
        if samples:
            scene.cycles.samples = samples
        # # Set start and end frames for animation.
        # if frames:
        #     scene.frame_start = max(frames[0], scene.frame_start)
        #     f1 = (frames[1] < 0) * (scene.frame_end + 1) + frames[1]
        #     scene.frame_end = min(f1, scene.frame_end)
        # Set output path.
        scene.render.filepath = "//%s.png" % scene.name
        # Render.
        # bpy.ops.render.render(animation=frames, write_still=not frames)
        bpy.ops.render.render(animation=False, write_still=True)
        # Print device/setting again after rendering.
        print(bcups.compute_device_type, bcups.compute_device,
              scene.cycles.device)

    # Local nicknames.
    bcups = bpy.context.user_preferences.system
    # Select the compute device and set it to render to that one
    if device_t in gpu_devices:
        # Device selection.
        bcups.compute_device_type = device_t
        # Print devices
        print(bcups.compute_device_type, bcups.compute_device)
        if not bcups.compute_device.startswith(device_t):
            raise DeviceError("Failed to set compute device: %s" % device_t)
        device = "GPU"
    else:
        # Device selection.
        bcups.compute_device_type = "NONE"
        # Print devices
        print(bcups.compute_device_type, bcups.compute_device)
        if not bcups.compute_device.startswith("CPU"):
            raise DeviceError("Failed to set compute device: CPU")
        device = "CPU"
    # Make the list of scenes.
    if scenes == []:
        scenes = [bpy.context.scene]
    else:
        scenes = bpy.data.scenes[slice(*scenes)]
    # Loop over scenes
    for scene in scenes:
        render(scene, device, samples)


if __name__ == "__main__":
    ## Cmd line interface.
    def is_int(s):
        """ Returns bool indicating whether s can be converted into an int."""
        try:
            int(s)
        except ValueError:
            x = False
        else:
            x = True
        return x

    def parse_scenes(S):
        if S:
            # Convert each to either a string or an int.
            X = int(S) if is_int(S) else S
        else:
            X = None
        return X

    # Get the input arguments.
    # All args.
    args0 = sys.argv
    # Relevant arguments.
    if "--" in args0:
        idx = args0.index("--")
    else:
        # Figure out which argument this script was.
        thisfile = os.path.basename(inspect.getfile(inspect.currentframe()))
        idx = args0.index(thisfile)
    args = args0[idx + 1:]
    # Parser object.
    parser = argparse.ArgumentParser(description="render_runner arguments.")
    # 'device' argument.
    devices = gpu_devices + ("CPU",)
    parser.add_argument(
        "--device", "-D", choices=devices,
        help="Specify compute device: (%s)" % (", ".join(devices)))
    # 'samples' argument.
    parser.add_argument(
        "--samples", default=None, type=int,
        help="Specify how many samples per render.")
    # 'scenes' argument.
    parser.add_argument(
        "--scenes", nargs="*", default=[], type=parse_scenes,
        help="Specify which scenes to render. No argument means all.")
    # Create parser and parse args.
    try:
        parsed = parser.parse_args(args)
    except:
        print("Failed to parse arguments.")
        BP()
    device_t = parsed.device
    samples = parsed.samples
    scenes = parsed.scenes
    # Render.
    run(device_t=device_t, samples=samples, scenes=scenes)
