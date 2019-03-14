#!/usr/bin/env python
# coding: utf-8

import os
import subprocess
from nipype import Workflow, Function, Node
from nipype.interfaces import afni

from PIL import Image as pImage
from IPython.display import Image as ipyImage

this_env = os.environ
my_dir = this_env['MYDIR']

#Set up test data set and base output directory
input_func_data = os.path.abspath(os.path.join(my_dir, 'Data/Graner_QA_tools/test_data/fmri/fmri_test_input.nii.gz'))
base_dir = os.path.join(my_dir, 'Data/Graner_QA_tools/test_output/QA_tools_dev_space/')

#Define the wrapper function to 3dTcat (that can accept an input file name that doesn't fully exist)
def cutTRs(input_data):
    import subprocess
    import os
    full_input_file = input_data+'[4..$]'
    input_name = os.path.split(input_data)[-1]
    prefix = "_cut"
    if input_name[-7:] == '.nii.gz':
        cut_output = input_name.split('.nii.gz')[0]+prefix+input_name[-7:]
    elif input_name[-4:] == '.nii':
        cut_output = input_name.split('.nii')[0]+prefix+input_name[-4:]
    else:
        raise RuntimeError('Input data file does not end in .nii or .nii.gz! -- cutTRs()')
    
    cut_output = os.path.join(os.getcwd(), cut_output)
    
    call = ['3dTcat',
            '-prefix', cut_output,
            full_input_file]
#    print('Calling:{}'.format(call))
    process = subprocess.Popen(call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return cut_output


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

#Create a flat graph of the workflow
wf.write_graph(graph2use='flat')

flat_graph_file = os.path.join(base_dir, 'quickstats', 'graph_detailed.png')
ipyImage(filename=flat_graph_file)

#Run the workflow
wf.run()