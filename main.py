#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This scripts shows how to use the topoplot_tools
to create an topoplot with images at specific locations

The locations to plot the images are defined in the position_filename with N electrodes
The image to paste in each position are defined in the image_filenames list with N images
"""

import topoplot_tools as topo

# Parameters
head_radius       = 1000                      # In pixels
scale_images      = 0.8                       # Scale applied to images 
crop_images       = [0, 200, 0, 0] # L U R D  # Images crop in pixels, L U R D 
image_filenames   = [r'./lena.png', r'./lena.png', r'./lena.png', r'./lena.png', 
                     r'./lena.png', r'./lena.png', r'./lena.png'] 

# Using Sperical coordinates
position_filename = r'./spherical_coords.sph'
output_filename   = r'./spherical_coords.png'
topo.plot_in_topoplot(head_radius, position_filename, image_filenames, 
                      xyz_format = '',
                      output_filename = output_filename, 
                      scale_images = scale_images, 
                      crop_images = crop_images)

# Using Cartesian coordinates
position_filename = r'./cartesian_coords_default.xyz'
output_filename   = r'./cartesian_coords_default.png'
topo.plot_in_topoplot(head_radius, position_filename, image_filenames, 
                      xyz_format = 'default',
                      output_filename = output_filename, 
                      scale_images = scale_images, 
                      crop_images = crop_images)

# Using Cartesian coordinates EEGLab
position_filename = r'./cartesian_coords_eeglab.xyz'
output_filename   = r'./cartesian_coords_eeglab.png'
topo.plot_in_topoplot(head_radius, position_filename, image_filenames, 
                      xyz_format = 'EEGLab',
                      output_filename = output_filename, 
                      scale_images = scale_images, 
                      crop_images = crop_images)
