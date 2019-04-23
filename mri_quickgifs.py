

##############################################################
#Description: generate some quick gifs of an input image and a few QC derivatives
#             to visually check basic image quality
#
#
#Usage: python3 -m mri_quickgifs raw_input [output_dir]
#
#Inputs:
#   raw_input: path and filename of a 4D .nii or .nii.gz image file
#   [output_dir]: path where things will get written. If not provided, defaults to current working directory.
#
#Outputs:
#   .../output_dir/quickgifs_[input_filename_prefix]/mriquickgifs_[input_filename_prefix].html:
#           HTML file displaying output gifs
#   .../output_dir/quickgifs_[input_filename_prefix]/pictures_gifs/
#           Output directory containing gifs
#   Gifs Created:
#           [input_filename_prefix]_center_x_3.gif: center slice of the input image along the x axis at each time point
#           [input_filename_prefix]_center_y_3.gif: center slice of the input image along the y axis at each time point
#           [input_filename_prefix]_center_z_3.gif: center slice of the input image along the z axis at each time point
#           [input_filename_prefix]_mean_1.gif: slices along the x axis of the temporal mean of the input image
#           [input_filename_prefix]_mean_2.gif: slices along the y axis of the temporal mean of the input image
#           [input_filename_prefix]_mean_3.gif: slices along the z axis of the temporal mean of the input image
#           [input_filename_prefix]_stdev_1.gif: slices along the x axis of the temporal standard deviation of the input image
#           [input_filename_prefix]_stdev_2.gif: slices along the y axis of the temporal standard deviation of the input image
#           [input_filename_prefix]_stdev_3.gif: slices along the z axis of the temporal standard deviation of the input image
#           [input_filename_prefix]_snr_1.gif: slices along the x axis of the temporal SNR (mean/stdev) of the input image
#           [input_filename_prefix]_snr_2.gif: slices along the y axis of the temporal SNR (mean/stdev) of the input image
#           [input_filename_prefix]_snr_3.gif: slices along the z axis of the temporal SNR (mean/stdev) of the input image
#           [input_filename_prefix]_cut_mean_1.gif: slices along the x axis of the temporal mean of the input image after removing 4 TRs
#           [input_filename_prefix]_cut_mean_2.gif: slices along the y axis of the temporal mean of the input image after removing 4 TRs
#           [input_filename_prefix]_cut_mean_3.gif: slices along the z axis of the temporal mean of the input image after removing 4 TRs
#           [input_filename_prefix]_cut_stdev_1.gif: slices along the x axis of the temporal standard deviation of the input image after removing 4 TRs
#           [input_filename_prefix]_cut_stdev_2.gif: slices along the y axis of the temporal standard deviation of the input image after removing 4 TRs
#           [input_filename_prefix]_cut_stdev_3.gif: slices along the z axis of the temporal standard deviation of the input image after removing 4 TRs
#           [input_filename_prefix]_cut_snr_1.gif: slices along the x axis of the temporal SNR (mean/stdev) of the input image after removing 4 TRs
#           [input_filename_prefix]_cut_snr_2.gif: slices along the y axis of the temporal SNR (mean/stdev) of the input image after removing 4 TRs
#           [input_filename_prefix]_cut_snr_3.gif: slices along the z axis of the temporal SNR (mean/stdev) of the input image after removing 4 TRs
#
#Development: (04/2019) Written by John Graner, Ph.D., LaBar Laboratory, Center for Cognitive Neuroscience, Duke University, Durham, NC, USA
##################################################################

from PIL import Image as pImage
import os, sys
import subprocess
import argparse
import nibabel as nib
import numpy as np
import imageio

#Set up argument parser and help dialogue
parser=argparse.ArgumentParser(
    description='''Generate quick visualization of input image and some basic statistical volumes. ''',
    usage='python3 -m mri_quickgifs raw_input_file [output_dir]')
parser.add_argument('raw_input_file', help='path and filename of a 4D .nii or .nii.gz')
parser.add_argument('output_dir', nargs='?', default=None, help='where things will get written. If not provided, uses current working dir')
args = parser.parse_args()


def _format_input_file(raw_input_file):
    #Check to see if the file was passed without a path.
    #If no path was included, append the current working directory.
    if os.path.split(raw_input_file)[0] == '':
        input_func_data = os.path.join(os.getcwd(), raw_input_file)
    else:
        input_func_data = raw_input_file
    return input_func_data


def _format_base_output_dir(dir_to_test, quickgifs_dir):
    #The passed directory needs to exist already
    if not os.path.exists(dir_to_test):
        print('Passed output directory not found: {}'.format(dir_to_test))
        raise RuntimeError
    return os.path.join(dir_to_test, quickgifs_dir)


def _get_niiprefext(input_nii):
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


def _grayscale_conv(input_array):
    #Convert an input array to 0-255 to support
    #grayscale png output
    gs_array = 255*(input_array/input_array.max())
    gs_array = np.rint(gs_array)
    return gs_array


def _format_picture(input_array, bot_rows_to_add=None):
    #The input will be an array as read by nib
    #The output will be a PIL Image object
    #Rotate the image (if needed) so the longest side is the width
    if input_array.shape[1] == max(input_array.shape):
        array_to_use = input_array
    else:
        array_to_use = np.rot90(input_array)

    if bot_rows_to_add is not None:
        array_to_use = np.concatenate((array_to_use, bot_rows_to_add),axis=0)

    pil_image = pImage.fromarray(array_to_use)
    #Convert the image mode to "LA" for writing
    output_pimage = pil_image.convert(mode="LA")
    return output_pimage


def _try_delete(file_to_go):
    if os.path.exists(file_to_go):
        os.remove(file_to_go)


def _write_html(input_prefix, output_dir):
    #Write out an html file to display the various gifs created.
    #For now, just assume a static set of gifs.

    if not os.path.exists(output_dir):
        print('Output directory not found: {} -- _write_html()'.format(output_dir))
        return None

    line_list = [
    '<HTML>', 
    '<HEAD>',
    '<TITLE>mri_quickgifs Summary</TITLE>',
    '</HEAD>',
    '<BODY>',
    '<H1>ORIGINAL IMAGE</H1>',
    '<H2>fMRI Center Slices Over Time</H2>',
    '<br>',
    '<IMAGE SRC=".\pictures_gifs\{}_center_x_3.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_center_y_3.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_center_z_3.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<br>',
    '<H2>Mean Image</H2>',
    '<br>',
    '<IMAGE SRC=".\pictures_gifs\{}_mean_1.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_mean_2.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_mean_3.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<br>',
    '<H2>Standard Deviation Image</H2>',
    '<br>',
    '<IMAGE SRC=".\pictures_gifs\{}_stdev_1.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_stdev_2.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_stdev_3.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<br>',
    '<H2>Temporal SNR Image</H2>',
    '<br>',
    '<IMAGE SRC=".\pictures_gifs\{}_snr_1.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_snr_2.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_snr_3.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<br>',
    '<H1>IMAGE WITH FIRST 4 TRS REMOVED</H1>',
    '<H2>Mean Image</H2>',
    '<br>',
    '<IMAGE SRC=".\pictures_gifs\{}_cut_mean_1.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_cut_mean_2.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_cut_mean_3.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<br>',
    '<H2>Standard Deviation Image</H2>',
    '<br>',
    '<IMAGE SRC=".\pictures_gifs\{}_cut_stdev_1.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_cut_stdev_2.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_cut_stdev_3.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<br>',
    '<H2>Temporal SNR Image</H2>',
    '<br>',
    '<IMAGE SRC=".\pictures_gifs\{}_cut_snr_1.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_cut_snr_2.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_cut_snr_3.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<br>',
    '</BODY>',
    '</HTML>'
    ]

    output_file = os.path.join(output_dir, 'mriquickgifs_{}.html'.format(input_prefix))
    with open(output_file, 'w') as fo:
        for line in line_list:
            fo.write('{}\n'.format(line))

    return output_file


def temp_stdev(input_nii, output_dir):
    
    input_prefix, extension = _get_niiprefext(input_nii)
    if (input_prefix == None) or (extension == None):
        print('Error getting input file prefix and/or extension!')
        return None
    suffix = '_stdev'

    #Put together output image
    output_file = os.path.join(output_dir, input_prefix+suffix+extension)

    #Delete the image if it already exists
    _try_delete(output_file)

    #Put together call to create standard deviation image
    call_parts = ['3dTstat', '-nzstdev', '-prefix', output_file, input_nii]
    process = subprocess.Popen(call_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return output_file


def temp_mean(input_nii, output_dir):
    
    input_prefix, extension = _get_niiprefext(input_nii)
    if (input_prefix == None) or (extension == None):
        print('Error getting input file prefix and/or extension!')
        return None
    suffix = '_mean'

    #Put together output image
    output_file = os.path.join(output_dir, input_prefix+suffix+extension)

    #Delete the image if it already exists
    _try_delete(output_file)

    #Put together call to create mean image
    call_parts = ['3dTstat', '-nzmean', '-prefix', output_file, input_nii]
    process = subprocess.Popen(call_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return output_file


def temp_cut(input_nii, output_dir):
    
    input_prefix, extension = _get_niiprefext(input_nii)
    if (input_prefix == None) or (extension == None):
        print('Error getting input file prefix and/or extension!')
        return None
    suffix = '_cut'

    #Put together output image
    output_file = os.path.join(output_dir, input_prefix+suffix+extension)

    #Delete the image if it already exists
    _try_delete(output_file)

    #Put together call to create mean image
    call_parts = ['3dTcat', '-prefix', output_file, input_nii+'[4..$]']
    process = subprocess.Popen(call_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
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

    #Delete the image if it already exists
    _try_delete(output_file)

    #Put together call to create snr image
    call_parts = ['3dcalc', '-a', input_mean,
                            '-b', input_stdev,
                            '-float',
                            '-prefix', output_file,
                            '-exp', 'a/b']
    process = subprocess.Popen(call_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return output_file


def arr_to_gif(input_array, slice_dim, output_dir, output_gif_prefix, prog_rows_flag=0):
    #Scale the image to 0-255
    input_array = _grayscale_conv(input_array)

    #Transpose the data so we can always create slices along the
    #last dimension of the array.
    transpose_array = np.arange(3)
    transpose_array = np.roll(transpose_array, 3-slice_dim)

    data_to_slice = input_array.transpose(transpose_array)
    num_slices = data_to_slice.shape[-1]

    #If desired, create some rows to add to the bottom of the picture to
    #display progress through the gif
    if prog_rows_flag:
        longest_side = max(data_to_slice.shape[0:2])
        step_per_picture = float(longest_side)/float(num_slices)
        progress_indices = np.ceil(np.arange(num_slices)*step_per_picture)

    #Create pictures of each slice
    slice_files = []
    for slice_num in range(num_slices):
        slice_data = data_to_slice[:,:,slice_num]
        if prog_rows_flag:
            prog_rows = np.zeros((5, longest_side))
            prog_rows[:, 0:int(progress_indices[slice_num])] = 255
        else:
            prog_rows = None
        slice_to_write = _format_picture(slice_data, bot_rows_to_add=prog_rows)
        slice_outfile = os.path.join(output_dir, 'temp_slice_gif_{}.png'.format(slice_num))
        slice_to_write.save(slice_outfile)
        slice_files.append(slice_outfile)
    #Create a gif of the center slice pictures
    images = []
    for filename in slice_files:
        images.append(imageio.imread(filename))
    output_gif = os.path.join(output_dir, '{prefix}_{dim}.gif'.format(prefix=output_gif_prefix,dim=slice_dim))
    imageio.mimsave(output_gif, images, duration=0.1)
    #Delete pngs
    for filename in slice_files:
        _try_delete(filename)
    return output_gif


def niithree_to_gif(input_nii, slice_dim, output_dir, prog_rows_flag=0):
    #NOTE: this function assumes the input image has 3 dimensions

    #Make sure the input image exists
    if not os.path.exists(input_nii):
        print('Input nii cannot be found: {} -- niithree_to_gif()'.format(input_nii))
        return None

    #Read in mean nifti image as a nibabel image and get data
    img = nib.load(input_nii)
    img_data = img.get_data()

    output_gif_prefix = os.path.split(input_nii)[-1].split('.nii')[0]

    output_gif = arr_to_gif(img_data, slice_dim, output_dir, output_gif_prefix, prog_rows_flag=prog_rows_flag)
    
    return output_gif


def main(args):

    #Extract the passed argument as the input file
    raw_input_file=args.raw_input_file

    #If the input file name wasn't passed with a path, append the
    #current working directory.
    input_func_data = _format_input_file(raw_input_file)

    #Variable for this script's output directory
    input_prefix, input_extension = _get_niiprefext(input_func_data)
    quickgifs_dir = 'quickgifs_{}'.format(input_prefix)

    #See if an output directory was passed.
    if args.output_dir is not None:
        #Get passed output directory
        dir_to_test = args.output_dir
    else:
        #Set the output directory to the path of the input file
        dir_to_test = os.path.join(os.path.split(input_func_data)[0])

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

    #Create version of input image with first 4 timepoints removed
    print('Creating short version of input...')
    cut_nii = temp_cut(input_func_data, image_output_dir)
    if cut_nii is None:
        print('Error creating shorter input image!')
        print('Input file: {}'.format(input_func_data))
        raise RuntimeError

    #Create temporal standard deviation of cut image
    print('Creating temporal standard deviation of short image...')
    cut_stdev_nii = temp_stdev(cut_nii, image_output_dir)
    if cut_stdev_nii is None:
        print('Error creating standard deviation of cut image!')
        print('Input file: {}'.format(cut_nii))
        raise RuntimeError

    #Create temporal mean of cut image
    print('Creating temporal mean of short image...')
    cut_mean_nii = temp_mean(cut_nii, image_output_dir)
    if cut_mean_nii is None:
        print('Error creating mean of short image!')
        print('Input file: {}'.format(cut_nii))
        raise RuntimeError

    #Create temporal SNR of cut image
    print('Creating temporal SNR of short image...')
    cut_snr_nii = temp_snr(cut_mean_nii, cut_stdev_nii, image_output_dir)
    if cut_snr_nii is None:
        print('Error creating temporal SNR of short image!')
        print('Input Mean image: {}'.format(cut_mean_nii))
        print('Input Stdev image: {}'.format(cut_stdev_nii))
        raise RuntimeError

    ##Create gifs that go through the center slices at each timepoint##
    #Read in nifti as a nibabel image
    img = nib.load(input_func_data)

    #Get image data
    img_data = img.get_data()
    
    #Get the center slice number of each dimension
    img_dims = img_data.shape
    center_x = round(img_dims[0] / 2.0)
    center_y = round(img_dims[1] / 2.0)
    center_z = round(img_dims[2] / 2.0)
    time_points = img_dims[3]

    #Keep only the center slice of each dimension
    center_x_image = img_data[center_x, :, :, :]
    center_y_image = img_data[:, center_y, :, :]
    center_z_image = img_data[:, :, center_z, :]

    #Get the input image prefix
    input_prefix = os.path.split(input_func_data)[-1].split('.nii')[0]

    #Create gifs through time
    print('Creating center slice gifs...')
    center_x_gif = arr_to_gif(center_x_image, 3, picgifs_output_dir, '{}_center_x'.format(input_prefix), prog_rows_flag=1)
    center_y_gif = arr_to_gif(center_y_image, 3, picgifs_output_dir, '{}_center_y'.format(input_prefix), prog_rows_flag=1)
    center_z_gif = arr_to_gif(center_z_image, 3, picgifs_output_dir, '{}_center_z'.format(input_prefix), prog_rows_flag=1)

    ##Create gifs going through the mean image in each dimension
    print('Creating temporal mean gifs...')
    mean_gif_one = niithree_to_gif(mean_nii, 1, picgifs_output_dir)
    mean_gif_two = niithree_to_gif(mean_nii, 2, picgifs_output_dir)
    mean_gif_three = niithree_to_gif(mean_nii, 3, picgifs_output_dir)

    #Create gifs going through the stdev image
    print('Creating temporal standard deviation gifs...')
    stdev_gif_one = niithree_to_gif(stdev_nii, 1, picgifs_output_dir)
    stdev_gif_two = niithree_to_gif(stdev_nii, 2, picgifs_output_dir)
    stdev_gif_three = niithree_to_gif(stdev_nii, 3, picgifs_output_dir)

    #Create gifs going through the snr image
    print('Creating temporal SNR gifs...')
    snr_gif_one = niithree_to_gif(snr_nii, 1, picgifs_output_dir)
    snr_gif_two = niithree_to_gif(snr_nii, 2, picgifs_output_dir)
    snr_gif_three = niithree_to_gif(snr_nii, 3, picgifs_output_dir)

    #Create gifs going through the short mean image
    print('Creating temporal mean gifs for shortened image...')
    cut_mean_gif_one = niithree_to_gif(cut_mean_nii, 1, picgifs_output_dir)
    cut_mean_gif_two = niithree_to_gif(cut_mean_nii, 2, picgifs_output_dir)
    cut_mean_gif_three = niithree_to_gif(cut_mean_nii, 3, picgifs_output_dir)

    #Create gifs going through the short stdev image
    print('Creating temporal standard deviation gifs for shortened image...')
    cut_stdev_gif_one = niithree_to_gif(cut_stdev_nii, 1, picgifs_output_dir)
    cut_stdev_gif_two = niithree_to_gif(cut_stdev_nii, 2, picgifs_output_dir)
    cut_stdev_gif_three = niithree_to_gif(cut_stdev_nii, 3, picgifs_output_dir)

    #Create gifs going through the short snr image
    print('Creating temporal SNR gifs for shortened image...')
    cut_snr_gif_one = niithree_to_gif(cut_snr_nii, 1, picgifs_output_dir)
    cut_snr_gif_two = niithree_to_gif(cut_snr_nii, 2, picgifs_output_dir)
    cut_snr_gif_three = niithree_to_gif(cut_snr_nii, 3, picgifs_output_dir)

    #Delete the mean image, the stdev image, and the SNR image
    print('Deleting temporary images...')
    _try_delete(mean_nii)
    _try_delete(stdev_nii)
    _try_delete(snr_nii)
    _try_delete(cut_nii)
    _try_delete(cut_mean_nii)
    _try_delete(cut_stdev_nii)
    _try_delete(cut_snr_nii)

    #Delete the image output directory, which should now be empty
    if os.path.exists(image_output_dir):
        os.rmdir(image_output_dir)

    #Write out the html
    print('Writing output html file...')
    output_html = _write_html(input_prefix, output_dir)
    if output_html is None:
        print('Something went wrong creating html file! -- mri_quickgifs.main()')
        raise RuntimeError
    print('-------------------------------------------------')
    print('Output html file: {}'.format(output_html))
    print('-------------------------------------------------')

if __name__ == "__main__":
    main(args)