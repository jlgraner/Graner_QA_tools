# Graner_QA_tools

This repository is meant to house some basic MRI quality assurance tools.

## percsigchange.py
This script reads in various things from a FEAT output directory and calculates the voxel-wise percent signal change for a given EV of the design matrix.

### Installation/Setup (quick, "manual" option)
1. Clone/download the repository and save it somewhere in your python path or a place from which you can run python scripts. (Setup file creation is on the TODO list.)
2. Navigate to the repository directory and run ```pip install -r requirements.txt```

### Running the Script
1. Navigate to the directory containing percsigchange.py (if it's not in your python path).
2. ```python percsigchange.py [--event_height FLOAT] INPUT_FEAT_DIR EV_INDEX [OUTPUT_DIR]```
3. The script should take on the order of seconds to run (depending on the size of the input data).

INPUT_FILE: full path and file name of a completed FEAT directory<br><br>
--event_height INT (optional): passing a float to the event_height option will cause the script to use that value as the estimated height of an individual event in the design EV. If not passed, the script will calculate an estimate by subtracing the actual design matrix EV min from the design matrix EV max.<br><br>
EV_INDEX: Integer of the EV of interest in the design matrix.
OUTPUT_DIR (optional): full path to where you'd like percsigchange to save the resulting Nifti file. If no value is provided, the script defaults to the input FEAT directory.

### Methods
Percent signal change is calculated for a single EV for each voxel. This is done by first multiplying the EV's parameter estimate (e.g. "pe1.nii.gz") image by the estimated event height in the design matrix. This provides the signal change produced by the event of interest in units of raw signal intensity. This voxel-wise signal intensity is then converted by percent signal change by dividing by the temporal mean in each voxel.

### Output
The output is a 3D image called "peY_percchange.nii.gz", where Y is the EV index.
