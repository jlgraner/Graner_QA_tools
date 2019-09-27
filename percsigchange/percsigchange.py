

import os
import pandas as pd
import subprocess
import argparse



def __add_prefix(input_file, prefix):
    #This function appends a string to the existing prefix of an image file.
    #It assumes the image file is either .nii or .nii.gz.
    input_beginning, input_end = input_file.split('.nii')
    output_file = input_beginning+str(prefix)+'.nii'+input_end
    return output_file


def calc_perc_change(input_pe_file, mean_func_file, pe_range, output_dir):
    #Calculate the percent signal change image
    input_pe_name = os.path.split(input_pe_file)[-1]
    perc_change_name = __add_prefix(input_pe_name, '_percchange')
    perc_change_file = os.path.join(output_dir, perc_change_name)

    str_pe_range = '{:.5f}'.format(pe_range)

    calc_call = [
                 'fslmaths',
                 input_pe_file,
                 '-mul', str_pe_range,
                 '-div', mean_func_file,
                 '-mul', '100.0',
                 perc_change_file
                 ]
    try:
        calc_output = subprocess.run(calc_call, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print('ERROR with calculation of percent signal change image!')
        print('Call: {}'.format(' '.join(calc_call)))
        print('Process Messages: {}'.format(err.output))
        return None

    return perc_change_file


def calc_pe_scale(designmat_file, pe_index):
    #Convert the design.mat into a design.txt file
    designtxt_file = designmat_file[:-4]+'.txt' 

    convert_call = [
                    'Vest2Text',
                    designmat_file,
                    designtxt_file
                    ]
    if not os.path.exists(designtxt_file):
        try:
            convert_output = subprocess.run(convert_call, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            print('ERROR with conversion of design.mat to design.txt!')
            print('Call: {}'.format(' '.join(convert_call)))
            print('Process Messages: {}'.format(err.output))
            return None
    else:
        print('design.txt already there...')

    #Read in the contents of the design.txt file as a dataframe
    design_matrix = pd.read_csv(designtxt_file, sep='\t', header=None)

    #Calculate ev range
    pe_index = int(pe_index)-1
    pe_range = float(design_matrix.loc[:,pe_index].max()) - float(design_matrix.loc[:,pe_index].min())

    return pe_range


def generate_map(feat_dir, pe_index, output_dir=None, event_height=None):

    #Make sure the feat_dir exists
    print('Checking feat directory...')
    if not os.path.exists(feat_dir):
        raise RuntimeError('Passed feat_dir does not exist: {}'.format(feat_dir))

    #Make sure the output_dir exists, if passed
    print('Setting output directory...')
    if output_dir is not None:
        if not os.path.exists(output_dir):
            raise RuntimeError('Passed output_dir does not exist: {}'.format(output_dir))

    #If output_dir is None, set it to the feat_dir
    if output_dir is None:
        output_dir = feat_dir

    #Find and check the desired /stats/pe??.nii.gz file
    print('Checking PE image file...')
    input_pe_file = os.path.join(feat_dir, 'stats', 'pe{}.nii.gz'.format(pe_index))
    if not os.path.exists(input_pe_file):
        raise RuntimeError('pe stats file cannot be found: {}'.format(input_pe_file))

    #Find and check the mean_func.nii.gz file
    print('Checking mean func file...')
    mean_func_file = os.path.join(feat_dir, 'mean_func.nii.gz')
    if not os.path.exists(mean_func_file):
        raise RuntimeError('mean functional image file cannot be found: {}'.format(mean_func_file))

    if event_height is None:
        #Find and check the design.mat file
        print('Checking design.mat file...')
        designmat_file = os.path.join(feat_dir, 'design.mat')
        if not os.path.exists(designmat_file):
            raise RuntimeError('design.mat file cannot be found: {}'.format(designmat_file))

        #Calculate the pe design range
        print('Calculating PE design model range...')
        pe_range = calc_pe_scale(designmat_file, pe_index)
        if pe_range is None:
            raise RuntimeError('Error calculating PE range!')
    else:
        print('Event height passed: {:.5f}'.format(event_height))
        pe_range = float(event_height)

    #Create percent signal change image
    print('Creating percent signal change image...')
    perc_change_file = calc_perc_change(input_pe_file, mean_func_file, pe_range, output_dir)
    if perc_change_file is None:
        raise RuntimeError('Error creating percent signal change image!')

    print('Percent Signal Change Image: {}'.format(perc_change_file))

    

def main(args):
    
    feat_dir = str(args.feat_dir)
    pe_index = int(args.pe_index)
    if args.output_dir is not None:
        output_dir = str(args.output_dir)
    else:
        output_dir = args.output_dir
    if args.event_height is not None:
        event_height = float(args.event_height)
    else:
        event_height = None

    generate_map(feat_dir, pe_index, output_dir=output_dir, event_height=event_height)


if __name__ == "__main__":
    #Set up argument parser and help dialogue
    parser=argparse.ArgumentParser(
        description='''Generate a percent signal change image for a specific PE of a FEAT design. ''',
        usage='python3 -m percsigchange feat_dir pe_index [output_dir]')
    parser.add_argument('--event_height', help='height of a single event, as modeled by FSL; if not passed, it will be set as the max of the EV minus the min of the EV in the design matrix', default=None)
    parser.add_argument('feat_dir', help='.feat directory of the analysis')
    parser.add_argument('pe_index', help='index number of a PE in the design you wish to calculate a percent signal change map for (index begins at 1)')
    parser.add_argument('output_dir', nargs='?', default=None, help='where things will get written. If not provided, use feat directory')
    args = parser.parse_args()
    main(args)