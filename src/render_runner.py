""" Controls Blender rendering."""
import argparse
try:
    import bpy
except ImportError:
    bpy = None
import inspect
import os
import signal
import sys
#
from pdb import set_trace as BP


class DeviceError(Exception):
    pass


def kill_blender():
    """ Kill Blender process."""
    os.kill(os.getpid(), signal.SIGUSR1)


gpu_devices = ("CUDA", "OPENCL")


def blender_run(f_anim, device_t=None, scenes=False, samples=None, frame=None):
    """ Run rendering procedures."""

    def render(f_anim, scene, device, samples, frame):
        """ Set the scene and do the render."""
        # Set the rendering device.
        scene.cycles.device = device
        # Print device setting.
        print(scene.cycles.device)
        # Set number of samples.
        if samples:
            scene.cycles.samples = samples
        # Set frame.
        if frame is not None:
            scene.frame_current = frame
        # Set output path.
        scene.render.filepath = "//%s.png" % scene.name
        # Render.
        bpy.ops.render.render(animation=f_anim, write_still=not f_anim,
                              scene=scene.name)

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
    if scenes:
        if len(scenes) == 1:
            scenes = [bpy.data.scenes[scenes[0]]]
        else:
            scenes = bpy.data.scenes[slice(*scenes)]
    else:
        scenes = [bpy.context.scene]
    # Loop over scenes.
    for scene in scenes:
        render(f_anim, scene, device, samples, frame)


def run():
    """ Wrap all functionality in run() function to handle exceptions
    without going to Blender."""

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

    # Get first Python argument index: idx.
    try:
        idx = sys.argv.index("--") + 1
    except ValueError:
        # "--" isn't an argument, start with next argument after this script.
        # Determine which argument this script is.
        thisfile = os.path.basename(inspect.getfile(inspect.currentframe()))
        idx = None
        for i, a in enumerate(sys.argv):
            if os.path.basename(a) == thisfile:
                idx = i + 1
        if idx is None:
            raise argparse.ArgumentError("Cannot split argument list.")
    # The Python script's arguments.
    args = sys.argv[idx:]
    # Description for parser.
    try:
        description = __doc__
    except NameError:
        description = ""
    # Parser object.
    parser = argparse.ArgumentParser(description=description)
    # Argument: f_anim.
    parser.add_argument(
        "--render-anim", "-a", action="store_true", default=False,
        help="Render frames from start to end.")
    # Argument: device.
    devices = gpu_devices + ("CPU",)
    parser.add_argument(
        "--device", "-D", choices=devices,
        help="Sets compute device: (%s)" % (", ".join(devices)))
    # Argument: samples.
    parser.add_argument(
        "--samples", default=None, type=int,
        help="Sets number of samples per render.")
    # Argument: scenes.
    parser.add_argument(
        "--scenes", nargs="*", default=[], type=parse_scenes,
        help="List of scene names or indices to render. Defaults to none.")
    # Argument: frame.
    parser.add_argument(
        "--render-frame", "-f", default=None, type=int,
        help="Sets frame to render.")
    # Argument: f_no_kill.
    parser.add_argument(
        "--no-kill", action="store_true", default=False,
        help="Will not kill Blender at the end of this script.")
    # Create parser and parse args.
    try:
        parsed, remaining = parser.parse_known_args(args)
    except SystemExit as err:
        if not err.code:
            # Normal exit occurred, probably from "--help". Just kill
            # Blender now, because otherwise it will continue running
            # (and probably print Blender's help to stdout).
            kill_blender()
        else:
            # Abnormal exit.
            # Re-raise error.
            raise err
            # Exit script and exit Blender.
            sys.exit(err.code)
            bpy.ops.wm.quit_blender()
            BP()
            kill_blender()
    # Get parsed arguments.
    f_anim = parsed.render_anim
    device_t = parsed.device
    samples = parsed.samples
    scenes = parsed.scenes
    frame = parsed.render_frame
    f_kill = not parsed.no_kill
    if bpy:
        # Render.
        blender_run(f_anim, device_t=device_t, samples=samples, scenes=scenes,
                    frame=frame)
    else:
        print("** Called from outside Blender. Exiting. **")
    # Kill blender. This script is intended to be used as a final
    # command line arguments to Blender because there's Really no good
    # way to consume the Python arguments and then return to take more
    # Blender arguments. Command line arg "--no-kill" can be used to
    # avoid this.
    if f_kill:
        kill_blender()


if __name__ == "__main__":
    ## Cmd line interface.
    try:
        run()
    except:
        print("\n\nError generated from Python script.")
        BP()
