#!/usr/bin/env python
""" Converts an .exr (OpenEXR format) file's depth channgel to a .png.
http://www.blender.org/forum/viewtopic.php?p=98212&sid=4cef7d0c329b3c3fe366e66832482fc0

Peter Battaglia
2013.04.08
"""
# Standard
from argparse import ArgumentError, ArgumentParser
import glob
from math import log10
from operator import add
import os
import sys
# External
import Imath
import OpenEXR
import numpy as np
from scipy.misc import imsave
#
from pdb import set_trace as BP


def load_exr(filename):
    """ Loads .exr file."""
    exrimg = OpenEXR.InputFile(filename)
    return exrimg


def get_exr_dims(exrimg):
    dw = exrimg.header()['dataWindow']
    width = dw.max.x - dw.min.x + 1
    height = dw.max.y - dw.min.y + 1
    return width, height


def get_channels(exrimg, outchans="RGBA"):
    """ Get the separate channels.
    Possible values are: R, G, B, A, Z"""
    def fromstr(s, width, height):
        mat = np.fromstring(s, dtype=np.float16)
        mat = mat.reshape(height, width)
        return mat

    w, h = get_exr_dims(exrimg)
    pt = Imath.PixelType(Imath.PixelType.HALF)
    channels = [fromstr(s, w, h) for s in exrimg.channels(outchans, pt)]
    return channels


def convert(infilename, outfilename, outchans, normalize, nanfill):
    """ Convert one file."""
    # Load the .exr file.
    exrimg = load_exr(infilename)
    # Get the channels.
    channels = get_channels(exrimg, outchans=outchans)
    # Compose image data into what is necessary for output.
    outimg = np.squeeze(np.dstack(channels))
    # Fix nans and infs.
    badidx = ~np.isfinite(outimg)
    if np.any(badidx):
        outimg[badidx] = nanfill
    # Normalize (optionally).
    if normalize:
        outimg /= outimg.max()
        # Reset any nanfill values that were changed by normalizing.
        # what was specified.
        outimg[badidx] = nanfill
    # Write output file.
    imsave(outfilename, outimg)


if __name__ == "__main__":
    # Parse input arguments.

    ## Cmd line interface.
    # Create parser object.
    parser = ArgumentParser(description="Output options.")
    # Argument: input file name.
    parser.add_argument("innames", nargs="+", help="Input filename(s).")
    # Argument: output file name.
    parser.add_argument("-o", dest="outname", default="",
                        help=("Output file name. If extension is "
                              "present, it overrides the default."))
    # Argument: output file format.
    parser.add_argument("-f", dest="outfmt", default=None,
                        help="Output file format. Overrides default.")
    # Argument: output file channels.
    parser.add_argument("-c", dest="outchans",
                        default="RGBA", help="Output channels.")
    # Argument: Z-channel for output file.
    parser.add_argument("-Z", action="store_true",
                        help="Output normalized Z channel. Same as -C Z -n.")
    # Argument: normalize output image.
    parser.add_argument("-n", dest="normalize", action="store_true",
                        help="Normalize output image.")
    # Argument: default value to fill nans with.
    parser.add_argument("--nanfill", default=-1,
                        help="Value to replace nans with.")
    # Create parser and parse args.
    parsed = parser.parse_args()
    innames = reduce(add, [sorted(glob.glob(fn)) for fn in parsed.innames])
    outname = parsed.outname
    outfmt = parsed.outfmt
    outchans = parsed.outchans
    normalize = parsed.normalize
    nanfill = parsed.nanfill
    ## Set parameters according to inputs.
    N = len(innames)
    if N == 0:
        raise IOError("Cannot find input files that match: %s" %
                      ", ".join(parsed.innames))
    # Output format.
    if outfmt is None:
        # If no outfmt was input, try getting it from the outname.
        outfmt = os.path.splitext(outname)[1].lstrip(".")
        if not outfmt:
            # If outname also doesn't specify outfmt, default to .png.
            outfmt = "png"
    # Output file's base name without extension.
    outname = os.path.splitext(outname)[0]
    # Output file names.
    nametemplate = "%%s_%%0%dd" % (int(log10(N)) + 1)
    outnames = []
    for i, inname in enumerate(innames):
        if not outname:
            # If outname is empty, use the inname.
            on = os.path.splitext(inname)[0]
        else:
            # If outname was supplied, use it and append count if
            # there is more than one inname.
            if N == 1:
                on = outname
            else:
                on = nametemplate % (outname, i)
        outnames.append("%s.%s" % (on, outfmt))
    # If "-Z" flag was input, override outchans.
    if parsed.Z:
        outchans = "Z"
    # Run the converter over all files.
    for inname, outname in zip(innames, outnames):
        # Make sure we're not overwriting the input file.
        if inname == outname:
            raise ValueError("Attempted to overwrite: %s" % inname)
        # Do the conversion.
        convert(inname, outname, outchans, normalize, nanfill)
