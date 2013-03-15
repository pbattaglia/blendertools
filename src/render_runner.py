import sys, bpy
import inspect, os

def run(switch=None, f_scenes=False, f_anim=False, frame_rng=()):
    # Local nicknames
    bcups = bpy.context.user_preferences.system

    def render(scene):
        # Make scene active
        bpy.context.screen.scene = scene
        # Select the compute device and set it to render to that one
        if switch == 'CUDA':
            # Device selection
            bcups.compute_device_type = 'CUDA'
            # Print devices
            print(bcups.compute_device_type, bcups.compute_device)
            assert bcups.compute_device.startswith('CUDA'), "** CUDA failed **"
            # Render setting
            scene.cycles.device = 'GPU'
        elif switch == 'OPENCL':
            # Device selection
            bcups.compute_device_type = 'OPENCL'
            # Print devices
            print(bcups.compute_device_type, bcups.compute_device)
            assert(bcups.compute_device.startswith('OPENCL'),
                   "** OPENCL failed **")
            # Render setting
            scene.cycles.device = 'GPU'
        else:
            # Device selection
            bcups.compute_device_type = 'NONE'
            # Print devices
            print(bcups.compute_device_type, bcups.compute_device)
            assert bcups.compute_device == 'CPU', "** CPU failed **"
            # Render setting
            scene.cycles.device = 'CPU'
        # Print device setting
        print(scene.cycles.device)
        # Set start and end frames for animation
        if f_anim and frame_rng:
            scene.frame_start = max(scene.frame_start, frame_rng[0])
            mx = (frame_rng[1]
                  if frame_rng[1] > 0 else scene.frame_end + frame_rng[1] + 1)
            scene.frame_end = min(scene.frame_end, mx)
        # Set number of samples
        scene.cycles.samples = 1000
        scene.render.filepath = "//%s.png" % scene.name
        ## Render
        f_still = True #not f_anim
        bpy.ops.render.render(animation=f_anim, write_still=f_still)
        # Print device/setting again, post render
        print(bcups.compute_device_type, bcups.compute_device,
              scene.cycles.device)

    # Handle multiple scenes
    if f_scenes:
        scenes = bpy.data.scenes[:]
    else:
        scenes = [bpy.context.scene]

    # Loop over scenes
    for scene in scenes:
        render(scene)


# Main
if __name__ == "__main__":
    args = sys.argv

    # Get relevant arguments
    if "--" in args:
        idx = args.index("--")
    else:
        # script filename (usually with path)
        thisfile = os.path.basename(inspect.getfile(inspect.currentframe()))
        idx = args.index(thisfile)
    pargs = args[idx + 1:]

    # Which render device?
    if len(pargs) > 0:
        switch = pargs[0]
    else:
        switch = None
    # Scene?
    if len(pargs) > 1:
        f_scenes = pargs[1] == "True"
    else:
        f_scenes = False

    # Animate?
    if len(pargs) > 2:
        f_anim = pargs[2] == "True"
    else:
        f_anim = False
    # Which frame?
    if len(pargs) > 3:
        frame_rng = tuple([int(f) for f in pargs[3:5]])
    else:
        frame_rng = (1, -1)

    # import pdb
    # pdb.set_trace()

    # Run render
    run(switch=switch, f_scenes=f_scenes, f_anim=f_anim, frame_rng=frame_rng)
