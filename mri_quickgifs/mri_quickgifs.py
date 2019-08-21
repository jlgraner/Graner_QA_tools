

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
#History: (04/2019) Written by John Graner, Ph.D., LaBar Laboratory, Center for Cognitive Neuroscience, Duke University, Durham, NC, USA
##################################################################

from PIL import Image as pImage
import os, sys
import subprocess
import argparse
import nibabel as nib
import numpy as np
from scipy import signal
import imageio

#Set up argument parser and help dialogue
parser=argparse.ArgumentParser(
    description='''Generate quick visualization of input image and some basic statistical volumes. ''',
    usage='python3 -m mri_quickgifs raw_input_file [output_dir]')
parser.add_argument('--cuttrs', help='set number of trs to exclude (i.e. pre-steady-state trs)', default=0)
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


def _grayscale_conv(input_array, perc=None):
    #Convert an input array to 0-255 to support
    #grayscale png output
    if perc is not None:
        max_val = np.percentile(input_array, perc)
    else:
        max_val = input_array.max()

    gs_array = 255*(input_array/max_val)
    gs_array[np.where(gs_array>255)] = 255

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


def _write_html(input_prefix, output_dir, cuttrs):
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
    '<H1>Note: The first {} TRs were removed from the data before creating these movies.</H1>'.format(cuttrs),
    '<H2>fMRI Center Slices Over Time</H2>',
    '<br>',
    '<IMAGE SRC=".\pictures_gifs\{}_center_x_3.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_center_y_3.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<IMAGE SRC=".\pictures_gifs\{}_center_z_3.gif" HEIGHT=200 ALT="gif_test">'.format(input_prefix),
    '<br>',
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


def arr_to_gif(input_array, slice_dim, output_dir, output_gif_prefix, prog_rows_flag=0):
    #Scale the image to 0-255
    input_array = _grayscale_conv(input_array, perc=99.95)

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


def main(args):

    #Extract the number of TRs to cut (default is 0)
    cuttrs = int(args.cuttrs)

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
    picgifs_output_dir = os.path.join(output_dir, 'pictures_gifs')
    if not os.path.exists(picgifs_output_dir):
        print('Creating asset output directory: {}'.format(picgifs_output_dir))
        os.mkdir(picgifs_output_dir)

    #Read the input file in as a nibabel image object
    input_img = nib.load(input_func_data)
    input_data = input_img.get_data()
    ##TODO: Check the shape of the input data (should be 4D)
    print('Removing first {} timepoints...'.format(cuttrs))
    cut_data = input_data[:,:,:,cuttrs:]

    #Detrend data and create temporal standard deviation images
    print('Detrending input data...')
    detrend_data = signal.detrend(input_data, axis=3, type='linear')
    detrend_cut = signal.detrend(cut_data, axis=3, type='linear')
    print('Creating temporal standard deviation image...')
    stdev_data = np.std(detrend_data, axis=3)
    stdev_cut = np.std(cut_data, axis=3)

    #Create temporal mean image
    print('Creating temporal mean image...')
    mean_data = np.mean(input_data, axis=3)
    mean_cut = np.mean(cut_data, axis=3)

    #Create temporal SNR image
    print('Creating temporal SNR image...')
    tsnr_data = np.zeros(mean_data.shape)
    tsnr_data = np.divide(mean_data, stdev_data, out=tsnr_data, where=stdev_data!=0)
    tsnr_cut = np.zeros(mean_cut.shape)
    tsnr_cut = np.divide(mean_cut, stdev_cut, out=tsnr_cut, where=stdev_cut!=0)

    ##Create gifs that go through the center slices at each timepoint##
    #Get the center slice number of each dimension
    img_dims = cut_data.shape
    center_x = round(img_dims[0] / 2.0)
    center_y = round(img_dims[1] / 2.0)
    center_z = round(img_dims[2] / 2.0)
    time_points = img_dims[3]

    #Keep only the center slice of each dimension
    center_x_image = cut_data[center_x, :, :, :]
    center_y_image = cut_data[:, center_y, :, :]
    center_z_image = cut_data[:, :, center_z, :]

    #Get the input image prefix
    input_prefix = os.path.split(input_func_data)[-1].split('.nii')[0]

    #Create gifs through time
    print('Creating center slice gifs...')
    center_x_gif = arr_to_gif(center_x_image, 3, picgifs_output_dir, '{}_center_x'.format(input_prefix), prog_rows_flag=1)
    center_y_gif = arr_to_gif(center_y_image, 3, picgifs_output_dir, '{}_center_y'.format(input_prefix), prog_rows_flag=1)
    center_z_gif = arr_to_gif(center_z_image, 3, picgifs_output_dir, '{}_center_z'.format(input_prefix), prog_rows_flag=1)

    ##Create gifs going through the mean image in each dimension
    print('Creating temporal mean gifs...')
    mean_gif_one = arr_to_gif(mean_cut, 1, picgifs_output_dir, '{}_cut_mean'.format(input_prefix), prog_rows_flag=0)
    mean_gif_two = arr_to_gif(mean_cut, 2, picgifs_output_dir, '{}_cut_mean'.format(input_prefix), prog_rows_flag=0)
    mean_gif_three = arr_to_gif(mean_cut, 3, picgifs_output_dir, '{}_cut_mean'.format(input_prefix), prog_rows_flag=0)

    #Create gifs going through the stdev image
    print('Creating temporal standard deviation gifs...')
    stdev_gif_one = arr_to_gif(stdev_cut, 1, picgifs_output_dir, '{}_cut_stdev'.format(input_prefix), prog_rows_flag=0)
    stdev_gif_two = arr_to_gif(stdev_cut, 2, picgifs_output_dir, '{}_cut_stdev'.format(input_prefix), prog_rows_flag=0)
    stdev_gif_three = arr_to_gif(stdev_cut, 3, picgifs_output_dir, '{}_cut_stdev'.format(input_prefix), prog_rows_flag=0)

    #Create gifs going through the snr image
    print('Creating temporal SNR gifs...')
    snr_gif_one = arr_to_gif(tsnr_cut, 1, picgifs_output_dir, '{}_cut_snr'.format(input_prefix), prog_rows_flag=0)
    snr_gif_two = arr_to_gif(tsnr_cut, 2, picgifs_output_dir, '{}_cut_snr'.format(input_prefix), prog_rows_flag=0)
    snr_gif_three = arr_to_gif(tsnr_cut, 3, picgifs_output_dir, '{}_cut_snr'.format(input_prefix), prog_rows_flag=0)

    #Write out the html
    print('Writing output html file...')
    output_html = _write_html(input_prefix, output_dir, cuttrs)
    if output_html is None:
        print('Something went wrong creating html file! -- mri_quickgifs.main()')
        raise RuntimeError
    print('-------------------------------------------------')
    print('Output html file: {}'.format(output_html))
    print('-------------------------------------------------')

if __name__ == "__main__":
    main(args)