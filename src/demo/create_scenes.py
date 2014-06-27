"""Make Blender scenes from .scene files.
Peter Battaglia
2014.03
"""
import bpy
import json
import math
import os
import sys


THICKNESS = 0.12


def load_scenes(filenames):
    """Load scenes from `filenames` and return."""
    scenes = []
    for fn in filenames:
        with open(fn, 'r') as fid:
            scene = json.load(fid)
        scenes.append(scene)
    return scenes


def create_scene(name=None, mode='LINK_OBJECTS', thickness=THICKNESS):
    """ Create a new scene."""
    bpy.ops.scene.new(type=mode)  # Create the scene.
    scene = bpy.context.screen.scene
    if name is not None:
        scene.name = name  # Name the scene.
    # Animation parameters: how many frames and which to set as active.
    scene.frame_start = 1
    scene.frame_end = 5
    scene.frame_current = 1
    # Set the container's size.
    scene.objects['Container'].scale[1] = thickness / 2. * 1.05
    scene.objects['Container'].location[1] = thickness / 2.
    return scene


def create_poly(poly, thickness=THICKNESS):
    """Create a polyhedron. Start with a circle, with the same number
    of vertices as the poly, and extend it in depth.
    """
    n_verts = len(poly)  # Number of vertices.
    # Create a circle with the same number of vertices as the poly.
    bpy.ops.mesh.primitive_circle_add(vertices=n_verts, fill_type='NGON',
                                      rotation=(math.pi / 2., 0, 0))
    # Get handle of the new circle.
    active = bpy.context.scene.objects.active
    if len(active.data.vertices) != n_verts:
        # Something went wrong, and the active object doesn't have the
        # correct number of vertices.
        raise ValueError('Number of vertices do not match: {} != {}'.
                         format(len(active.data.vertices), n_verts))
    # Modify the circle's vertices coordinates to match the poly's.
    extrude = False
    for i, vo in enumerate(poly):
        vc = active.data.vertices[i].co
        vc.x = vo[0]
        vc.y = vo[1]
        try:
            vc.z = vo[2]
        except IndexError:
            # If `poly` doesn't provide all of the z-coordinates, then
            # we will just create the 3D object by extruding the x,y
            # coordinates.
            vc.z = 0
            extrude |= True
    if extrude:
        # Extrude the poly to make it 3D.
        bpy.ops.object.editmode_toggle()  # Extrude is an edit mode operation.
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate={'value': (0, thickness, 0)})  # Do extrude.
        bpy.ops.object.editmode_toggle()
    return active


def create_polys(polys, thickness=THICKNESS):
    """Create all of the polys."""
    for ipoly, poly in enumerate(polys):
        active = create_poly(poly, thickness=thickness)
        active.name = 'Poly_{:02d}'.format(ipoly)  # Name it.
        # Set its material.
        bpy.ops.object.material_slot_add()
        active.data.materials[0] = bpy.data.materials['Stone']
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent()
        bpy.ops.uv.smart_project()
        bpy.ops.object.editmode_toggle()


def assemble(scene_data, name, thickness=THICKNESS):
    """Create a new scene that contains the specified scene data."""
    # Remember the initial scene.
    scene0 = bpy.context.scene
    bpy.context.screen.scene = scene0
    scene = create_scene(name=name)
    create_polys(scene_data['polys'], thickness=thickness)
    # Set back to original scene.
    bpy.context.screen.scene = scene0


if __name__ == '__main__':
    from argparse import ArgumentParser
    scenes_dir0 = ('scenes')
    parser = ArgumentParser()
    parser.add_argument('--scenes_dir', default=scenes_dir0)
    try:
        args = sys.argv[sys.argv.index('--') + 1:]
    except ValueError:
        args = []
    parsed = parser.parse_known_args(args)[0]
    scenes_dir = parsed.scenes_dir
    ld = os.listdir(scenes_dir)
    names = [f.rsplit('.', 1)[0] for f in ld if f.rsplit('.')[1] == 'scene']
    filenames = [os.path.join(scenes_dir, f) for f in os.listdir(scenes_dir)]
    scenes = load_scenes(filenames)

    for scene, name in zip(scenes, names):
        assemble(scene, name)    
