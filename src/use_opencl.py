""" Sets render device for every scene to: OPENCL."""
import bpy


class DeviceError(Exception):
    pass


def set_device(device):
    """ Sets rendering device."""
    # Local nickname.
    bcups = bpy.context.user_preferences.system
    # Device selection.
    bcups.compute_device_type = device[0]
    if not bcups.compute_device.startswith(device[0]):
        raise DeviceError("Failed to set compute device: %s" % device[0])
    # Loop over scenes
    for scene in bpy.data.scenes:
        setattr(scene.cycles, "device", device[1])


device = ("OPENCL", "GPU")
set_device(device)
