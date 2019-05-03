# Graner_QA_tools

This repository is meant to house some basic MRI quality assurance tools.

## mri_quickgifs.py
This script reads in a 4D .nii or .nii.gz file, creates gifs that visualize:
1. The center slice for each axis across each time point.
2. All slices across each axis for the temporal mean image, the temporal standard deviation image, and the temporal SNR image.
3. The same as number 2 but calculated after the first 4 time points of the image have been removed (to possibly account for non-steady state TRs).

### Installation/Setup (quick, "manual" option)
1. Clone/download the repository and save it somewhere in your python path or a place from which you can run python scripts. (Setup file creation is on the TODO list.)
2. Navigate to the repository directory and run ```pip install -r requirements.txt```

### Installation via Docker
#### UNDER CONSTRUCTION

### Running the Script
1. Navigate to the directory containing mri_quickgifs.py (if it's not in your python path).
2. ```python mri_quickgifs.py INPUT_FILE [OUTPUT_DIR]```
3. The script should take on the order of 30 seconds to run (depending on the size of the input data).

INPUT_FILE: full path and file name of your 4D .nii or .nii.gz file<br><br>
OUTPUT_DIR (optional): full path to where you'd like mri_quickgifs to save the resulting gifs and html file. If no value is provided, the script defaults to the directory of the input image. NOTE: in either case the script will create a new "quickgifs" directory inside the output directory.

### Output
The primary output of the script is an html file in .../OUTPUT_DIR/quickgifs/ that will display the gif movies mentioned in the description above. The gifs themselves will be saved in .../OUTPUT_DIR/quickgifs/pictures_gifs/.

When finished, the script will display the name of the html file created in the terminal window. Open it with your favorite web browser.
