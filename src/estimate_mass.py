""" Estimate an object's mass and inertia attributes using particle
samples."""
import bmesh
import bpy
from contextlib import contextmanager


def add_particle_system(count=5000):
    """ Adds a particle system and sets some basic settings."""
    # Add the particle system.
    bpy.ops.object.particle_system_add()
    # Set its parameters.
    psd = bpy.data.particles[-1]
    psd.count = count
    psd.frame_end = 1
    psd.lifetime = 1
    psd.emit_from = "VOLUME"
    psd.distribution = "RAND"
    psd.physics_type = "NO"


def remove_particle_system():
    """ Remove the particle system."""
    bpy.ops.object.particle_system_remove()


@contextmanager
def particle_system(obj=None):
    """ Context manager for adding/removing particle system."""
    # Store initial active object.
    obj0 = bpy.context.scene.objects.active
    if obj is not None:
        # Switch to input obj if one was provided.
        bpy.context.scene.objects.active = obj
    # Add the particle system.
    add_particle_system()
    # Return the active object on entry.
    yield bpy.context.scene.objects.active
    # Remove the particle system.
    remove_particle_system()
    # Set active object back to the initial one.
    bpy.context.scene.objects.active = obj0


def get_com_moi(obj=None):
    """ Get center-of-mass and moments of inertia."""
    with particle_system(obj=obj) as pobj:
        # Get particle system.
        ps = pobj.particle_systems[-1]
        # Get positions of all particles.
        pos = []
        for p in ps.particles:
            pos.append(p.location[:])
        com = []
        p2 = []
        for i, p in enumerate(zip(*pos)):
            # Calculate center of mass of points.
            c = sum(p) / len(p)
            com.append(c)
            p2.append([(x - c) ** 2 for x in p])
        # Calculate moments of inertia.
        moi = [sum(y + z for y, z in zip(p2[1], p2[2])),
               sum(x + z for x, z in zip(p2[0], p2[2])),
               sum(x + y for x, y in zip(p2[0], p2[1]))]
    return com, moi


def to_convex(obj):
    """ Replace obj's current mesh with its convex hull."""
    # Initialize new BMesh.
    bm = bmesh.new()
    # Set up the BMesh from the obj.
    bm.from_object(obj, bpy.context.scene)
    # Make convex hull.
    bmesh.ops.convex_hull(bm, input=bm.verts)
    # Update object's mesh.
    bm.to_mesh(obj.data)


@contextmanager
def convex_hull(obj=None):
    """ Context manager for adding/removing convex hull."""
    # Store initial active and selected objects.
    obja = bpy.context.scene.objects.active
    objs = bpy.context.selected_objects
    if obj is not None:
        # Switch to input obj if one was provided.
        bpy.context.scene.objects.active = obj
    # Clear selected objects.
    bpy.ops.object.select_all(action="DESELECT")
    # Select active obj.
    bpy.context.scene.objects.active.select = True
    # Duplicate selected objects.
    bpy.ops.object.duplicate()
    objd = bpy.context.scene.objects.active
    # Add the convex hull.
    to_convex(objd)
    # Return the active object on entry.
    yield objd
    # Delete the duplicate.
    bpy.ops.object.delete()
    # Set active and selected objects back to the initial one.
    bpy.context.scene.objects.active = obja
    for o in objs:
        o.select = True
