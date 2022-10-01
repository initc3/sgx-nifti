#!/usr/bin/env python3

import os

import nibabel as nib
import numpy as np

from nibabel.testing import data_path


#example_filename = os.path.join(data_path, 'example4d.nii.gz')

print("loading image ...")
img = nib.load("/opt/data/in/nifti/example4d.nii.gz")

print(f"image shape: {img.shape}")
#print(f"image data type is 16-bit signed integer: {img.get_data_dtype() == np.dtype(np.int16)}")
print(f"img.affine.shape: {img.affine.shape}")

# The complete information embedded in an image header is available via a format-specific header object.
hdr = img.header
print(f"image header: {hdr}")

print("In case of this NIfTI file it allows accessing all NIfTI-specific information, e.g.")
print(f"xyzt units: {hdr.get_xyzt_units()}")

#print(img.__dict__)
#print(dir(img))
#print(f"{'slicer' in dir(img)}")
#print(f"{'slicer' in img.__dir__()}")

cropped_img = img.slicer[32:-32, ...]
print("cropping imaging ... img.slicer[32:-32, ...]")
print(f"cropped image: {cropped_img.shape}")

nib.save(img, '/opt/data/out/nifti/cropped.nii')
