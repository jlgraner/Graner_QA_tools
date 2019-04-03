#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Testing out creating a gif from nii data in python3


# In[92]:


import nibabel as nib
from PIL import Image as pImage
import os, sys
import imageio


# In[93]:


import numpy as np


# In[94]:


def _grayscale_conv(input_array):
    gs_array = 255*(input_array/input_array.max())
    gs_array = np.rint(gs_array)
    return gs_array


# In[95]:


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


# In[96]:


test_data = '/mnt/keoki/experiments2/Graner/Data/Graner_QA_tools/test_data/fmri/fmri_test_input.nii.gz'


# In[98]:


#Load image with nibabel; get image data
input_image = nib.load(test_data)
input_data = input_image.get_data()


# In[100]:


#Create slice-wise sections of data
#Pick out the center slice of each time point for each dimension
#(We don't need to know which dimension is which since we're doing all of them)
input_dims = input_data.shape
center_x = round(input_dims[0] / 2.0)
center_y = round(input_dims[1] / 2.0)
center_z = round(input_dims[2] / 2.0)
time_points = input_dims[3]


# In[101]:


#Keep only the center slice of each dimension
center_x_image = input_data[center_x, :, :, :]
center_y_image = input_data[:, center_y, :, :]
center_z_image = input_data[:, :, center_z, :]


# In[102]:


#Rescale the image to 0-255 to support grayscale output
#test = 255*(center_x_image/center_x_image.max())
#test_int = np.rint(test)
test_int = _grayscale_conv(center_x_image)


# In[103]:


#Take out a test slice to write
test_slice = test_int[:,:,1]


# In[104]:


#Convert the slice to mode "LA" so it can be written to a png
#pil_to_write = test_pil.convert(mode='LA')
pil_to_write = _format_picture(test_slice)


# In[105]:


#Look at the slice
pil_to_write


# In[106]:


#Write the rotated slice to a file
#NOTE: the picture will be set to display at a decent size
#      in the html file
pil_to_write.save(os.path.join(os.getcwd(), 'test_slice.png'))


# In[ ]:




