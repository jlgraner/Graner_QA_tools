

#Goal: generate some quick gifs of an input image and a few QC derivatives
#      to visually check basic image quality



from PIL import Image as pImage
import os, sys
import subprocess
import nibabel as nib
import numpy as np
import imageio

args = sys.argv

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


def _format_picture(input_array):
    #The input will be an array as read by nib
    #The output will be a PIL Image object
    pil_image = pImage.fromarray(input_array)
    #Rotate the image (if needed) so the longest side is the width
    if pil_image.size[0] == max(pil_image.size):
        output_pimage = pil_image
    else:
        output_pimage = pil_image.rotate(90,expand=1)
    #Convert the image mode to "LA" for writing
    output_pimage = output_pimage.convert(mode="LA")
    return output_pimage


def temp_stdev(input_nii, output_dir):
    
    input_prefix, extension = _get_niiprefext(input_nii)
    if (input_prefix == None) or (extension == None):
        print('Error getting input file prefix and/or extension!')
        return None
    suffix = '_stdev'

    #Put together output image
    output_file = os.path.join(output_dir, input_prefix+suffix+extension)

    ##TODO: DELETE IMAGE IF IT ALREADY EXISTS

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

    ##TODO: DELETE IMAGE IF IT ALREADY EXISTS

    #Put together call to create mean image
    call_parts = ['3dTstat', '-nzmean', '-prefix', output_file, input_nii]
    error_flag = subprocess.call(call_parts)
    if error_flag:
        print('Mean creation failed: {}'.string.join(call_parts))
        return None
    return output_file


def temp_cut(input_nii, output_dir):
    
    input_prefix, extension = _get_niiprefext(input_nii)
    if (input_prefix == None) or (extension == None):
        print('Error getting input file prefix and/or extension!')
        return None
    suffix = '_cut'

    #Put together output image
    output_file = os.path.join(output_dir, input_prefix+suffix+extension)

    ##TODO: DELETE IMAGE IF IT ALREADY EXISTS

    #Put together call to create mean image
    call_parts = ['3dTcat', '-prefix', output_file, input_nii+'[4..$]']
    error_flag = subprocess.call(call_parts)
    if error_flag:
        print('TR cut failed: {}'.string.join(call_parts))
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

    ##TODO: DELETE IMAGE IF IT ALREADY EXISTS

    #Put together call to create snr image
    call_parts = ['3dcalc', '-a', input_mean,
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


def arr_to_gif(input_array, slice_dim, output_dir, output_gif_prefix):
    #Scale the image to 0-255
    input_array = _grayscale_conv(input_array)

    #Transpose the data so we can always create slices along the
    #last dimension of the array.
    transpose_array = np.arange(3)
    transpose_array = np.roll(transpose_array, 3-slice_dim)

    data_to_slice = input_array.transpose(transpose_array)
    num_slices = data_to_slice.shape[-1]

    #Create pictures of each slice
    slice_files = []
    for slice_num in range(num_slices):
        slice_data = data_to_slice[:,:,slice_num]
        slice_to_write = _format_picture(slice_data)
        slice_outfile = os.path.join(output_dir, 'temp_slice_gif_{}.png'.format(slice_num))
        slice_to_write.save(slice_outfile)
        slice_files.append(slice_outfile)
    #Create a gif of the center slice pictures
    images = []
    for filename in slice_files:
        images.append(imageio.imread(filename))
    output_gif = os.path.join(output_dir, '{prefix}_{dim}.gif'.format(prefix=output_gif_prefix,dim=slice_dim))
    print(output_gif)
    imageio.mimsave(output_gif, images, duration=0.1)
    #Delete pngs
    for filename in slice_files:
        try_delete(filename)
    return output_gif


def niithree_to_gif(input_nii, slice_dim, output_dir):
    #NOTE: this function assumes the input image has 3 dimensions

    #Make sure the input image exists
    if not os.path.exists(input_nii):
        print('Input nii cannot be found: {} -- niithree_to_gif()'.format(input_nii))
        return None

    #Read in mean nifti image as a nibabel image and get data
    img = nib.load(input_nii)
    img_data = img.get_data()

    output_gif_prefix = os.path.split(input_nii)[-1].split('.nii')[0]

    output_gif = arr_to_gif(img_data, slice_dim, output_dir, output_gif_prefix)
    
    return output_gif


def try_delete(file_to_go):
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
    print('Cutting first 4 timepoints...')
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
    center_x_gif = arr_to_gif(center_x_image, 3, picgifs_output_dir, '{}_center_x'.format(input_prefix))
    center_y_gif = arr_to_gif(center_y_image, 3, picgifs_output_dir, '{}_center_y'.format(input_prefix))
    center_z_gif = arr_to_gif(center_z_image, 3, picgifs_output_dir, '{}_center_z'.format(input_prefix))

    ##Create gifs going through the mean image in each dimension
    mean_gif_one = niithree_to_gif(mean_nii, 1, picgifs_output_dir)
    mean_gif_two = niithree_to_gif(mean_nii, 2, picgifs_output_dir)
    mean_gif_three = niithree_to_gif(mean_nii, 3, picgifs_output_dir)

    #Create gifs going through the stdev image
    stdev_gif_one = niithree_to_gif(stdev_nii, 1, picgifs_output_dir)
    stdev_gif_two = niithree_to_gif(stdev_nii, 2, picgifs_output_dir)
    stdev_gif_three = niithree_to_gif(stdev_nii, 3, picgifs_output_dir)

    #Create gifs going through the snr image
    snr_gif_one = niithree_to_gif(snr_nii, 1, picgifs_output_dir)
    snr_gif_two = niithree_to_gif(snr_nii, 2, picgifs_output_dir)
    snr_gif_three = niithree_to_gif(snr_nii, 3, picgifs_output_dir)

    #Create gifs going through the short mean image
    cut_mean_gif_one = niithree_to_gif(cut_mean_nii, 1, picgifs_output_dir)
    cut_mean_gif_two = niithree_to_gif(cut_mean_nii, 2, picgifs_output_dir)
    cut_mean_gif_three = niithree_to_gif(cut_mean_nii, 3, picgifs_output_dir)

    #Create gifs going through the short stdev image
    cut_stdev_gif_one = niithree_to_gif(cut_stdev_nii, 1, picgifs_output_dir)
    cut_stdev_gif_two = niithree_to_gif(cut_stdev_nii, 2, picgifs_output_dir)
    cut_stdev_gif_three = niithree_to_gif(cut_stdev_nii, 3, picgifs_output_dir)

    #Create gifs going through the short snr image
    cut_snr_gif_one = niithree_to_gif(cut_snr_nii, 1, picgifs_output_dir)
    cut_snr_gif_two = niithree_to_gif(cut_snr_nii, 2, picgifs_output_dir)
    cut_snr_gif_three = niithree_to_gif(cut_snr_nii, 3, picgifs_output_dir)

    #Delete the mean image, the stdev image, and the SNR image
    try_delete(mean_nii)
    try_delete(stdev_nii)
    try_delete(snr_nii)
    try_delete(cut_nii)
    try_delete(cut_mean_nii)
    try_delete(cut_stdev_nii)
    try_delete(cut_snr_nii)

    #Write out the html
    output_html = _write_html(input_prefix, output_dir)
    if output_html is None:
        print('Something went wrong creating html file! -- mri_quickgifs.main()')
        raise RuntimeError

if __name__ is "__main__":
    main(args)