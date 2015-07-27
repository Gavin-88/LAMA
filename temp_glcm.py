#!/usr/bin/env python

"""
This is just a temp file to test out the GLCM code on some mutants.

If it works, incorpoate  into reg_stats.py. But make reg_stats a class and subclass for each stats method as it's
getting a bit out of hand
"""
from scipy import stats

import harwellimglib as hil
from utilities.glcm3d import Glcm
import numpy as np
import SimpleITK as sitk

CHUNKSIZE = 10

def run(wt_dir, mut_dir, output_img):
    wts = hil.GetFilePaths(wt_dir)
    muts = hil.GetFilePaths(mut_dir)

    shape = sitk.GetArrayFromImage(sitk.ReadImage(wts[0])).shape

    print 'getting et glcms'
    wt_contrasts = []
    for wt in wts:
        glcm_maker = Glcm(wt)
        wt_contrasts.append(glcm_maker.get_contrasts())

    print "getting mut glcms"
    mut_contrasts = []
    for mut in muts:
        glcm_maker = Glcm(mut)
        mut_contrasts.append(glcm_maker.get_contrasts())

    print 'doing stats'
    print 'doing stats'
    wt_stacked = np.vstack(wt_contrasts)
    mut_stacked = np.vstack(mut_contrasts)

    raw_stats = stats.ttest_ind(wt_stacked, mut_stacked, axis=1)

    # reform a 3D array from the stas and write the image
    out_array = np.zeros(shape)

    i = 0

    for z in range(0, shape[0] - CHUNKSIZE, CHUNKSIZE):
        print 'w', z
        for y in range(0, shape[1] - CHUNKSIZE, CHUNKSIZE):
            for x in range(0, shape[2] - CHUNKSIZE, CHUNKSIZE):
                out_array[z: z + CHUNKSIZE, y: y + CHUNKSIZE, x: x + CHUNKSIZE] = raw_stats[i]
                i += 1

    out = sitk.GetImageFromArray(out_array)
    sitk.WriteImage(out, output_img)





if __name__ == '__main__':
    import sys
    wt_dir = sys.argv[1]
    mut_dir = sys.argv[2]
    output_img = sys.argv[3]
    run(wt_dir, mut_dir, output_img)
