# -*- coding: utf-8 -*-
"""
Scripts to plot images in a topoplot
"""

import numpy as np
import csv
from PIL import Image
from PIL import ImageDraw

def read_csv_position(filename, xyz_format='default'):
    '''
    Reads a text file CSV or tab-separated with the position information for the electrodes
    
    The text file can be in:
        Cartetian coordinates (X, Y, Z), or
        Geographic / Spetical coodinates as in EEGLab (sph_theta, sph_phi, sph_radius)
    
    The text file has to have headers
    
    Parameters
    ----------
    
    filename : Text file with locations
    xyz_format : Only needed for cartesian coordiantes, this indicated the XYZ definition:
                'default'  X is the axis from Left to Right ear
                           Y is the axis from inion (back) to nasion (front) of the head 
                           Z is the axis from the bottom to top of the head
                
                'EEGLab'   X is the axis from inion (back) to nasion (front) of the head 
                           Y is the axis from Left to Right ear
                           Z is the axis from the bottom to top of the head                          
    Returns
    -------
    
    info_electrodes : List of dictionaries with the position information for each electrode
    
    '''
    # detect delimiter and presence of headers
    with open(filename, 'r') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect)
        has_header = csv.Sniffer().has_header(csvfile.read(1024))
    
    if not has_header:
        print('The provided CSV has not headers')
        return 
    
    # read headers
    reader = csv.reader(open(filename, 'r'), dialect=dialect)
    headers = reader.__next__()
    header_tuples = []
    for ix, header in enumerate(headers):
        if header != '':
            header_tuples.append((ix, header))
    
    # electrode information to dictionary
    info_electrodes = []
    for row in reader:
        d = {}
        for header_tuple in header_tuples:
            try:
                d[header_tuple[1]] = float(row[header_tuple[0]])
            except:
                d[header_tuple[1]] = row[header_tuple[0]]    
        info_electrodes.append(d)
    
    # verify fields for geographic coordinates (sph_theta, sph_phi, sph_radius)
    if 'sph_phi' in info_electrodes[0] and 'sph_theta' in info_electrodes[0]:
        if not 'sph_radius' in info_electrodes[0]:
            for info_electrode in info_electrodes:
                info_electrode['sph_radius'] = 1
        return info_electrodes
    
    if 'X' in info_electrodes[0] and 'Y' in info_electrodes[0] and 'Z' in info_electrodes[0]:
        for info_electrode in info_electrodes:
            x = info_electrode['X']
            y = info_electrode['Y']
            z = info_electrode['Z']
            # XYZ, to geographic / spherical coordinates
            r_xy = np.sqrt(x**2 + y**2)
            if xyz_format == 'default':
                info_electrode['sph_theta'] = np.arctan2(x, y) * 180 / np.pi
            elif xyz_format == 'EEGLab':    
                info_electrode['sph_theta'] = np.arctan2(y, x) * 180 / np.pi
            
            info_electrode['sph_phi'] = np.arctan2(z, r_xy) * 180 / np.pi
            info_electrode['sph_radius'] = 1
        return info_electrodes

def draw_circle_thick(centerxy, radius, im, outline_color, thickness):
    '''
    Draws a circle with centre 'centerxy' (array) and radius 'radius'
    the color of the circle is 'outline_color', and thickness of 'thikness pixels'
    
    Parameters
    ----------
    
    centerxy       : X,Y coordinates for the center of the circle
    radius         : radius of the circle in pixels
    im             : image to draw in
    outline_color  : color of the circle
    thickness      : thickness of the circle in pixels
    
    Returns
    -------

    im : Image with drawn circle
    
    '''    
    # Solid circle
    im = draw_circle_center(centerxy, radius, im, outline_color, outline_color)
    # Inside transparent circle
    im = draw_circle_center(centerxy, radius-thickness, im, outline_color)
    return im

def draw_circle_center(centerxy, radius, im, outline_color, fill_color=(255,255,255,0)):
    '''
    Draws as solid circle centered at centerxy
    
    Parameters
    ----------
    
    centerxy       : X,Y coordinates for the center of the circle
    radius         : radius of the circle in pixels
    im             : image to draw in
    outline_color  : color of the circle
    fill_color     : color of the filling
    
    Returns
    -------

    im : Image with drawn circle
    '''
    
    
    corners = tuple(centerxy - radius) + tuple(centerxy + radius)
    draw = ImageDraw.Draw(im)
    draw.ellipse(corners, fill=fill_color, outline=outline_color)
    return im

def pol2cart(theta_radius, centerxy):
    '''
    Polar 2D cordinates Theta and radius to X,Y coordinates
    for topoplot plots
    
    Parameters
    ----------
    
    theta_radius   : tuple with (Theta, radius)
    centerxy       : center of reference 
    
    Returns
    -------
    return         : array [X, Y]
        
    '''
    x = theta_radius[1] * np.cos((theta_radius[0] - 90) *  np.pi / 180)
    y = theta_radius[1] * np.sin((theta_radius[0] - 90) *  np.pi / 180)  
    return np.array([x, y]) + centerxy

def draw_paste(im, im_tmp, point_cart):
    '''
    Pastes an image 'im_tmp' into an image 'im'
    'im_tmp' is pasted such as its center is located at 'point_cart'
    
    Parameters
    ----------
    
    im         : host image
    im_tmp     : image to paste
    point_cart : where the image will be pasted
    
    Returns
    -------
    im         : host image with pasted image

    '''
    size_tmp = im_tmp.size;
    box = (point_cart[0].astype(int) - size_tmp[0] // 2, 
           point_cart[1].astype(int) - size_tmp[1] // 2,
           point_cart[0].astype(int) - size_tmp[0] // 2 + size_tmp[0], 
           point_cart[1].astype(int) - size_tmp[1] // 2 + size_tmp[1]) 
    im.paste(im_tmp, box)
    return im

def plot_in_topoplot(head_radius_pxs, position_filename, image_filenames, xyz_format = 'default', output_filename='./result.png', scale_images=1, crop_images=[]):
    '''
    Pastes an image 'im_tmp' into an image 'im'
    'im_tmp' is pasted such as its center is located at 'point_cart'
    
    Parameters
    ----------
    
    head_radius_pxs     : radius of head plot in pixels 
    position_filename   : text file with the position of electrodes
    image_filenames     : list with fullpath of the images to paste
    xyz_format          : XYZ format to read cartesian coordinates, see read_csv_position()
    output_filename     : fullpath for the output image
    scale_images        : scale factor for the image to paste
    crop_images         : indicates if the original images (without scale) will be cropped
    
    Returns
    -------
    output_filename     : fullpath for the output image

    '''
    
    #%% get electrode positions
    info_electrodes = read_csv_position(position_filename, xyz_format)  
    
    #%% canvas properties
    linewidth     = 5
    canvas_size   = np.array([2.5 * head_radius_pxs, 2.5 * head_radius_pxs]).astype(int)
    canvas_center = (0.5 * canvas_size).astype(int)

    # new image, full of transparent white
    im = Image.new('RGBA', tuple(canvas_size), color=(255, 255, 255, 0))
    
    #%% draw head with nose and ears
    # draw circle
    im = draw_circle_thick(canvas_center, head_radius_pxs, im, (0, 0, 0, 255), linewidth)
    draw = ImageDraw.Draw(im)
    # draw nose    
    nose_points = np.array([[-10, head_radius_pxs - linewidth],
                            [  0, head_radius_pxs * 1.2],
                            [ 10, head_radius_pxs - linewidth]]).astype(int)
    for i_point in range(nose_points.shape[0] - 1):
        line_tuple_ini = tuple(pol2cart(nose_points[i_point], canvas_center)) 
        line_tuple_fin = tuple(pol2cart(nose_points[i_point + 1], canvas_center))
        draw.line(line_tuple_ini + line_tuple_fin, fill=(0, 0, 0, 255), width = linewidth)
    
    # draw ears
    # values from EEGLAB topoplot function    
    r = np.array([0.50 , 0.52 , 0.53 , 0.54 ,	0.55 , 0.54 , 0.55 , 0.54 , 0.52 , 0.50]).reshape(-1,1)
    t = np.array([0.19 , 0.22 , 0.22 , 0.21 ,	0.17 ,-0.01 ,-0.16 ,-0.24 ,-0.26 ,-0.24]).reshape(-1,1)
    
    # scale to head_radius
    r = head_radius_pxs * r * 2
    # angles to Deg and refered to Nose
    t = (t * 180 / np.pi) + 90
    
    for side in [1 , -1]:
        ear_points = np.concatenate((side*t,r), axis=1)
        for i_point in range(ear_points.shape[0] - 1):
            line_tuple_ini = tuple(pol2cart(ear_points[i_point], canvas_center)) 
            line_tuple_fin = tuple(pol2cart(ear_points[i_point + 1], canvas_center))
            draw.line(line_tuple_ini + line_tuple_fin, fill=(0, 0, 0, 255), width = linewidth)
    
    #%% draw points and electrode names for each electrode location
    for info_electrode in info_electrodes:
        point_cart = pol2cart((info_electrode['sph_theta'], head_radius_pxs * info_electrode['sph_radius'] * np.cos(info_electrode['sph_phi'] * np.pi / 180 )), canvas_center)
        draw_circle_center(point_cart, 10, im, (0, 0, 0, 255), (0, 0, 0, 255))
     
    #%% draw stuff for each electrode location
    for info_electrode, image_filename in zip(info_electrodes, image_filenames):
        point_cart = pol2cart((info_electrode['sph_theta'], head_radius_pxs * info_electrode['sph_radius'] * np.cos(info_electrode['sph_phi'] * np.pi / 180 )), canvas_center)
        # load image
        im_tmp = Image.open(image_filename)
        # size 
        size_im = im_tmp.size
        # crop
        if crop_images != []:
            crop_box = (0 + crop_images[0], 0 + crop_images[1], size_im[0] - crop_images[2], size_im[1] - crop_images[3] )    
            im_tmp = im_tmp.crop(crop_box)
        # scale
        if scale_images != 1:
            im_tmp = im_tmp.resize(( int(im_tmp.size[0] * scale_images), int(im_tmp.size[1] * scale_images)))
        # paste im_tmp in specific point
        im = draw_paste(im, im_tmp, point_cart)
        
    #%% save image
    im.save(output_filename)
    print(output_filename)
    return output_filename