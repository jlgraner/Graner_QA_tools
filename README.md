# Graner_QA_tools

This repository is meant to house some basic MRI quality assurance tools.

## mri_quickgifs.py
This script reads in a 4D .nii or .nii.gz file and creates some gifs for very basic visual QA.
<br>
It produces gifs of:
1. The center slice for each axis across each time point.
2. All slices across each axis for the temporal mean image, the temporal standard deviation image, and the temporal SNR image.
3. The same as number 2 but calculated after the first 4 time points of the image have been removed (to possibly account for non-steady state TRs).

