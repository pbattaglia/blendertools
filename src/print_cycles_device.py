""" Prints Cycles device."""
import bpy


if __name__ == "__main__":
    # Print device settings.
    bcups = bpy.context.user_preferences.system
    print(bcups.compute_device_type, bcups.compute_device)
    print(bpy.context.scene.cycles.device)

