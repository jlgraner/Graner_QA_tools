

#Goal: generate some quick gifs of an input image and a few QC derivatives
#      to visually check basic image quality



from PIL import Image as pImage
import os, sys
import subprocess
import nibabel as nib
import numpy as np

args = sys.argv

this_env = os.environ

def _check_inputs(args):
    if len(args) < 2:
        print('Requires one input argument: file name of input .nii or .nii.gz image')
        return 0
    return 1


def _format_input_file(raw_input_file):
    #Check to see if the file was passed without a path.
    #If no path was included, append the current working directory.
    if os.path.split(raw_input_file)[0] == '':
        input_func_data = os.path.join(os.getcwd(), raw_input_file)
    else:
        input_func_data = raw_input_file
    return input_func_data

def _get_niiprefext(input_file):
    #Returns the prefix and extension of an input file after
    #determining if the ends in ".nii.gz" or ".nii".
    if input_nii[-7:] == '.nii.gz':
        extension = '.nii.gz'
        input_prefix = os.path.split(input_nii)[-1][:-7]
    elif input_nii[-3:] == '.gz':
        extension = '.gz'
        input_prefix = os.path.split(input_nii)[-1][:-3]
    else:
        print('Input file extension not recognized! Should be .nii or .nii.gz!')
        print('Instead is: {}'.format(os.path.splitext(input_nii)[-1]))
        return None, None
    return input_prefix, extension


def temp_stdev(input_nii, output_dir):
    
    input_prefix, extension = _get_niiprefext(input_nii)
    if (input_prefix == None) or (extension == None):
        print('Error getting input file prefix and/or extension!')
        return None
    suffix = '_stdev'

    #Put together output image
    output_file = os.path.join(output_dir, input_prefix+suffix+extension)

    #Put together call to create standard deviation image
    call_parts = ['3dTstat', '-nzstdev', '-prefix', output_file, input_nii]
    error_flag = subprocess.call(call_parts)
    if error_flag:
        print('Standard Deviation creation failed: {}'.string.join(call_parts))
        return None
    return output_file


def temp_mean(input_nii, output_dir):
    
    input_prefix, extension = _get_niiprefext(input_nii)
    if (input_prefix == None) or (extension == None):
        print('Error getting input file prefix and/or extension!')
        return None
    suffix = '_mean'

    #Put together output image
    output_file = os.path.join(output_dir, input_prefix+suffix+extension)

    #Put together call to create mean image
    call_parts = ['3dTstat', '-nzmean', '-prefix', output_file, input_nii]
    error_flag = subprocess.call(call_parts)
    if error_flag:
        print('Mean creation failed: {}'.string.join(call_parts))
        return None
    return output_file


def temp_snr(input_mean, input_stdev, output_dir):
    #TODO: Check input image format
    mean_prefix, mean_extension = _get_niiprefext(input_mean)
    if '_mean' in mean_prefix:
        output_prefix = mean_prefix.split('_mean')[0]
    else:
        output_prefix = mean_prefix
    suffix = '_snr'
    extension = mean_extension

    #Put together output image file
    output_file = os.path.join(output_dir, output_prefix+suffix+extension)

    #Put together call to create snr image
    call_parts = ['3dCalc', '-a', input_mean,
                            '-b', input_stdev,
                            '-float',
                            '-prefix', output_file,
                            '-exp', 'a/b']
    error_flag = subprocess.call(call_parts)
    if error_flag:
        print('SNR creation failed: {}'.string.join(call_parts))
        return None
    return output_file


def _format_base_output_dir(dir_to_test, quickgifs_dir):
    #The passed directory needs to exist already
    if not os.path.exists(dir_to_test):
        print('Passed output directory not found: {}'.format(dir_to_test))
        raise RuntimeError
    return os.path.join(dir_to_test, quickgifs_dir)


def main(args):

    #Variable for this script's output directory
    quickgifs_dir = 'quickgifs'

    #Check input arguments
    args_okay = _check_inputs(args)
    if not args_okay:
        ##TODO: Add error message output
        raise RuntimeError

    #Extract the passed argument as the input file
    raw_input_file = args[1]

    #If the input file name wasn't passed with a path, append the
    #current working directory.
    input_func_data = _format_input_file(raw_input_file)

    #See if an output directory was passed.
    if len(args) == 3:
        #Get passed output directory
        dir_to_test = args[2]
    else:
        #Set the output directory to the path of the input file plus "/quickgifs"
        dir_to_test = os.path.join(os.path.split(input_func_data)[0], quickgifs_dir)

    #Format output directory
    output_dir = _format_base_output_dir(dir_to_test, quickgifs_dir)

    #If the output directory doesn't exist, create it
    if not os.path.exists(output_dir):
        print('Creating output directory: {}'.format(output_dir))
        os.mkdir(output_dir)


    #Set some output subdirectories and create them if they're not there
    image_output_dir = os.path.join(output_dir, 'images')
    picgifs_output_dir = os.path.join(output_dir, 'pictures_gifs')
    for element in [image_output_dir, picgifs_output_dir]:
        if not os.path.exists(element):
            print('Creating asset output directory: {}'.format(element))
            os.mkdir(element)

    #Create temporal standard deviation image
    print('Creating temporal standard deviation image...')
    stdev_nii = temp_stdev(input_func_data, image_output_dir)
    if stdev_nii is None:
        print('Error creating standard deviation image!')
        print('Input file: {}'.format(input_func_data))
        raise RuntimeError

    #Create temporal mean image
    print('Creating temporal mean image...')
    mean_nii = temp_mean(input_func_data, image_output_dir)
    if mean_nii is None:
        print('Error creating mean image!')
        print('Input file: {}'.format(input_func_data))
        raise RuntimeError

    #Create temporal SNR image
    print('Creating temporal SNR image...')
    snr_nii = temp_snr(mean_nii, stdev_nii, image_output_dir)
    if snr_nii is None:
        print('Error creating temporal SNR image!')
        print('Input Mean image: {}'.format(mean_nii))
        print('Input Stdev image: {}'.format(stdev_nii))
        raise RuntimeError

    #Read in nifti as a nibabel image
    img = nib.load(input_func_data)

    #Get image data and affine transform
    img_data = img.get_data()
    img_affine = img.get_affine()
    
    #Create gif of center saggital slices
    #Create gif of center axial slices
    #Create gif of center coronal slices
    #Create gif going through mean image axially
    #Create gif going through mean image saggitally
    #Create gif going through mean image coronally



if __name__ is "__main__":
    main(args, this_env)