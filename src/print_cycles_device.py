""" Prints Cycles device."""
import bpy
from pdb import set_trace as BP


if __name__ == "__main__":
    # Print device settings.
    bcups = bpy.context.user_preferences.system
    bcupsbp = bcups.bl_rna.properties
    current_device_type = bcups.compute_device_type
    device_types = bcupsbp['compute_device_type'].enum_items.keys()
    devices = {}
    print('Devices:')
    for dt in device_types:
        bcups.compute_device_type = dt
        devices[dt] = bcupsbp['compute_device'].enum_items.keys()
        print('  {}: {}'.format(dt, ', '.join(devices[dt])))
    bcups.compute_device_type = current_device_type
    # print(bcups.compute_device_type, bcups.compute_device)
    # print(bpy.context.scene.cycles.device)

