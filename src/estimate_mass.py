""" Estimate an object's mass and inertia attributes using particle
samples."""
import bmesh
import bpy
from contextlib import contextmanager
from mathutils import Matrix, Vector
#
from pdb import set_trace as BP


def scale_matrix(vec):
    """ Creates a scale matrix from vec."""
    mat = Matrix()
    mat[0][0], mat[1][1], mat[2][2] = vec[:]
    return mat


def update(scene=None):
    """ Updates tags on scene."""
    if scene is None:
        scene = bpy.context.scene
    scene.update()


def aobj(obj=None):
    """ Return active object and (optionally) sets it to input 'obj'."""
    if obj is not None:
        bpy.context.scene.objects.active = obj
    return bpy.context.scene.objects.active


def add_particle_system(count=5000):
    """ Adds a particle system and sets some basic settings."""
    # Add the particle system.
    bpy.ops.object.particle_system_add()
    # Get handle to it and its settings.
    ps = aobj().particle_systems[-1]
    pss = ps.settings
    # Set its parameters.
    pss = aobj().particle_systems[-1].settings
    pss.count = count
    pss.frame_end = 1
    pss.lifetime = 1
    pss.emit_from = "VOLUME"
    pss.distribution = "RAND"
    pss.physics_type = "NO"
    update()
    return ps


def remove_particle_system():
    """ Remove the particle system."""
    bpy.ops.object.particle_system_remove()


@contextmanager
def particle_system(obj=None, count=5000):
    """ Context manager for adding/removing particle system."""
    # Store initial active object.
    obj0 = aobj()
    if obj is not None:
        # Switch to input obj if one was provided.
        aobj(obj)
    # Add the particle system.
    ps = add_particle_system(count=count)
    # Return the active object on entry.
    yield ps
    # Remove the particle system.
    remove_particle_system()
    # Set active object back to the initial one.
    aobj(obj0)


def get_com_moi(obj=None, count=5000):
    """ Get center-of-mass and moments of inertia."""
    with particle_system(obj=obj, count=count) as ps:
        # Get positions of all particles.
        pos = []
        for p in ps.particles:
            pos.append(p.location[:])
        com = []
        p2 = []
        for i, p in enumerate(zip(*pos)):
            # Calculate center of mass of points.
            c = sum(p) / count
            com.append(c)
            p2.append([(x - c) ** 2 for x in p])
        # Calculate moments of inertia.
        moi = [sum(y + z for y, z in zip(p2[1], p2[2])) / count,
               sum(x + z for x, z in zip(p2[0], p2[2])) / count,
               sum(x + y for x, y in zip(p2[0], p2[1])) / count]
    return com, moi


@contextmanager
def quaternion_mode(obj=None):
    """ Context manager for temporarily using quaternion mode for
    rotations."""
    if obj is None:
        obj = aobj()
    # Remember initial rotation_mode.
    mode = obj.rotation_mode
    # Set to QUATERNION.
    obj.rotation_mode = "QUATERNION"
    yield obj
    # Set back to initial rotation_mode.
    obj.rotation_mode = mode


# def get_center(obj):
#     """ Gets absolute center point of object's bounding box."""
#     # Compute object space center.
#     bb = obj.bound_box
#     mn = Vector([min(x) for x in zip(*bb)])
#     mx = Vector([max(x) for x in zip(*bb)])
#     ocenter = (mx + mn) / 2
#     # Get location and scale.
#     loc = obj.location
#     scl = obj.scale
#     # Get rotation matrix.
#     with quaternion_mode(obj):
#         rot = obj.rotation_quaternion.to_matrix()
#     # Compute center point.
#     center = rot * Vector([x * s for x, s in zip(ocenter, scl)]) + loc
#     return center


def to_bounding_box(obj):
    """ Replace obj's current mesh with its bounding box."""
    # Compute min and max along each axis.
    verts = [vert.co for vert in obj.data.vertices]
    mn = Vector([min(x) for x in zip(*verts)])
    mx = Vector([max(x) for x in zip(*verts)])
    # Compute scale and center.
    scale = mx - mn
    center = (mx + mn) / 2
    # Create translated scale matrix.
    mat = scale_matrix(scale)
    mat.translation = center
    # Initialize new BMesh.
    bm = bmesh.new()
    # Create the cube.
    bmesh.ops.create_cube(bm, size=1, matrix=mat)
    # Update object's mesh.
    bm.to_mesh(obj.data)


def to_convex_hull(obj):
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
def bounding_box(obj=None):
    """ Context manager for adding/removing bounding box."""
    # Store initial active and selected objects.
    obja = aobj()
    objs = bpy.context.selected_objects
    if obj is not None:
        # Switch to input obj if one was provided.
        aobj(obj)
    # Clear selected objects.
    bpy.ops.object.select_all(action="DESELECT")
    # Select active obj.
    aobj().select = True
    # Duplicate selected objects.
    bpy.ops.object.duplicate()
    objd = aobj()
    # Add the bounding box.
    to_bounding_box(objd)
    # Return the active object on entry.
    yield objd
    # Delete the duplicate.
    bpy.ops.object.delete()
    # Set active and selected objects back to the initial one.
    aobj(obja)
    for o in objs:
        o.select = True


@contextmanager
def convex_hull(obj=None):
    """ Context manager for adding/removing convex hull."""
    # Store initial active and selected objects.
    obja = aobj()
    objs = bpy.context.selected_objects
    if obj is not None:
        # Switch to input obj if one was provided.
        aobj(obj)
    # Clear selected objects.
    bpy.ops.object.select_all(action="DESELECT")
    # Select active obj.
    aobj().select = True
    # Duplicate selected objects.
    bpy.ops.object.duplicate()
    objd = aobj()
    # Add the convex hull.
    to_convex_hull(objd)
    # Return the active object on entry.
    yield objd
    # Delete the duplicate.
    bpy.ops.object.delete()
    # Set active and selected objects back to the initial one.
    aobj(obja)
    for o in objs:
        o.select = True
