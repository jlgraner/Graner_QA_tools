#!/usr/bin/env python
# coding: utf-8

#Write the temporary output images to a nipype directory structure
#Create jpegs and gifs
#Delete the temporary output images

import sys, os
from nipype import Workflow, Function, Node
from nipype.interfaces import afni
from PIL import Image as pImage
from IPython.display import Image as ipyImage

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

#Define the wrapper function to 3dTcat (that can accept an input file name that doesn't fully exist)
def cutTRs(input_data):
    import subprocess
    import os, string

    #Make sure the input data file ends in .nii or .nii.gz
    if not ((input_data[-7:] == '.nii.gz') or (input_data[-4:] == '.nii')):
        raise RuntimeError('Input data file does not end in .nii or .nii.gz! -- cutTRs()')

    full_input_file = input_data+'[4..$]'
    #Create the output file path/name
    input_path, input_name = os.path.split(input_data)
    suffix = "_cut"
    file_part = input_name.split('.')[0]
    # ending_part = string.join(input_name.split('.')[1:], '.')
    ending_part = '.'.join(input_name.split('.')[1:])
    new_name = file_part+suffix+'.'+ending_part
    
    cut_output = os.path.join(os.getcwd(), new_name)
    
    call = ['3dTcat',
            '-prefix', cut_output,
            full_input_file]
#    print('Calling:{}'.format(call))
    process = subprocess.Popen(call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return cut_output

def main(args):
    
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

    #Create the nipype base directory based on the location of this file


    #Set up test data set and base output directory
    base_dir = os.path.join(my_dir, 'Data/Graner_QA_tools/test_output/QA_tools_dev_space/')

    #Instantiate AFNI 3dTcat interface
    #tcatNode = afni.TCat()
    cutNode = Node(Function(input_names=['input_data'],
                        output_names=['cut_output'],
                        function=cutTRs),
               name='cut')

    #Set the input value for the cut node
    cutNode.inputs.input_data = input_func_data

    #Instantiate an AFNI 3dTstat node for calculating standard deviation
    stdevNode = Node(afni.TStat(args='-stdev', outputtype='NIFTI_GZ'), name='stdev')

    #Instantiate an AFNI 3dTstat node for calculating mean
    meanNode = Node(afni.TStat(args='-mean', outputtype='NIFTI_GZ'), name='mean')

    #Instantiate an AFNI 3dCalc node for calculating temporal SNR
    snrNode = Node(afni.Calc(expr='abs(a)/b', args='-float', outputtype='NIFTI_GZ'), name='snr')

    #Create a short workflow putting together the cut and stdev
    wf = Workflow(name='quickstats', base_dir=base_dir)
    #wf.connect(cut, 'cut_output', stdev, 'in_file')
    wf.connect([
        (cutNode, stdevNode, [('cut_output', 'in_file')]),
        (cutNode, meanNode, [('cut_output', 'in_file')]),
        (meanNode, snrNode, [('out_file', 'in_file_a')]),
        (stdevNode, snrNode, [('out_file', 'in_file_b')])
              ])

    #Run the workflow
    wf.run()

if __name__ is "__main__":
    main(args)