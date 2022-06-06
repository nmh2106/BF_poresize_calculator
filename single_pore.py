# -*- coding: utf-8 -*-
"""
Created on Fri Aug  6 13:07:07 2021

THIS VERSION ANALYZES ONE IMAGE AT A TIME!
Better when you have to tune the processing methods inbetween images
and if you want to observe the process more carefully.
"""
#%matplotlib inline
#%config Inlinebackend.figure_format = 'retina'
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.rcParams.update({'figure.figsize':(10,10), 'image.cmap':'gray'})
from scipy import ndimage as ndi
from skimage import io, util, exposure, filters, segmentation, morphology, color, measure
import pandas as pd
import openpyxl
import statistics
import csv



def contrast(img, scale, visualize):
    """Adjust contrast for given image 
    scale: values less than 1 DECREASE contrast, values more than 1 INCREASE contrast
    if visualize is set as True, the contrasted image will be displayed."""
    
    pores_gamma = exposure.adjust_gamma(img, scale)
    
    if visualize:
        plt.imshow(pores_gamma)
        #plt.title('Contrasted image')
        plt.show() #include, if image does not show with just imshow()
        
    return pores_gamma

def remove_noise(img, visualize):
    """Denoises an image with selected filtering method
    the level of noise removal CAN be changed by changing the parameter size
    on the line where the ndi.median_filter is called. Default here is size=6. 
    Can be made smaller or larger. Large values will take a long time to compute 
    and usually lead to a blurry image.
    Setting visualize as True displays the processed image.
    """
    
    denoised = ndi.median_filter(util.img_as_float(img), size=3)
       
    if visualize:
        plt.imshow(denoised)
        #plt.title('Denoised image')
        plt.show() #include if image does not show with just imshow()

    return denoised

def crop_bottom(img, level, visualize):
    """Strips SEM-info from the bottom of the image, i.e. all pixels under the given level
    visualize as True shows the cropped image"""
    
    cropped = img[:level, :]
    
    if visualize:
        plt.imshow(cropped)
        #plt.title('Cropped image')
        plt.axis('off')
        plt.show() #Include if image does not show with just imshow()
        
    return cropped

def threshold_filter(img, method, visualize):
    """Thresholding with an automatic filter, returns the binary image
    method chooses the used algorithm, and should be either put in as either:
    li
    mean
    triangle
    yen
    
    Setting visualize as True, will display the filtered image.
    """
    
    if method=='li':
        thresh = filters.threshold_li(img)
    elif method=='mean':
        thresh = filters.threshold_mean(img)
    elif method == 'triangle':
        thresh = filters.threshold_triangle(img)
    elif method == 'yen':
        thresh  = filters.threshold_yen(img)      
        
    thresholded = img <= thresh
    
    if visualize:
        plt.imshow(thresholded)
        #plt.title('Mask with threshold filter')
        plt.show() #Include if image does not show with just imshow()
        
    return thresholded

def threshold_handpicked(image, value, visualize):
    """Thresholding with a handpicked value, returns the binary image
    If returned image is just a white/black, it means that the hand-picked 
    value is either way too high or way too low. 
    
    If visualize is set as True, will display the binary image created 
    with the given threshold.
    """  
    thresholded = (image <= value)
    if visualize:
        plt.imshow(thresholded)
        #plt.title('Mask with handpicked threshold')
        plt.show()
    
    return thresholded

def shuffle_labels(labels):
    "Order of labels changed to help with visualization"
    indices = np.unique(labels[labels != 0])
    indices = np.append([0], np.random.permutation(indices))
    
    return indices[labels]

def main():
    
    nm_to_pixel = 0.0368 #Has to be measured with for example imageJ 
   
    file = '185_10k.tif' #Include name of the image file here. And path if not in the same directory as the script
    #Next few lines read the given image file. as_gray option should always be True to convert to gray scale, 
    #even if the (for example SEM) images appear grey as default
    img_name = file
    image = io.imread(img_name, as_gray= True)
    
    #Following reads the given experimental parameters into a dataframe
    #In order to include the experimental parameters for each sample into the final file
    #If this is not needed, the following 3 lines can be commented out. 
    #parameters = 'BF_experimental.xlsx'
    #df_params = pd.read_excel(parameters, skiprows=1)
    #df_params = df_params.set_index('Sample')
    
    
    #Output file, comment out the file where you do not want to write
    #i.e. if you want to KEEP the result, comment out trash
    #if you DO NOT WANT TO KEEP the result (and are for example testing) comment out the result file.
    #output_filename = 'results.csv'
    #output_filename = 'trash.csv'
    
    #if this is the first image for which results are saved, open the output file in WRITE-MODE 'w'
    #for ALL the images after that important to change back to APPEND-MODE 'a'
    #if not changed, it will overwrite over the previous results!!
    #output_file = open(output_filename, 'w')
    
    #If this this the first image that you're including into a file, comment in the next line (which has the output_file.write())
    #In orded to get the column names. (You can also change the column names)
    #Remember to COMMENT OUT the line if this is not the first image (otherwise the result file will have column names repeated between samples)
    
    #output_file.write('Sample,diameter,radius \n')
   
    #Strips extra characters from the given image name in order to get the sample number
    sample = file.lstrip('SEM_images\.')
    sample = int(sample.replace('_10k.tif', ''))
    
    #Finds parameters for the sample number from the dataframe
    #that was created from the 'BF_experimental file'
    #i.e. params variable will now contain a row of the dataframe 'df_params' for the sample    
    #params = df_params.loc[sample]
    
    #next lines get stuff from params, i.e. the experimental parameters for the sample
    #are saved into separate variables.    
    #bcp = params['BCP']       
    #nanop = params['Silica NPs size']
    #mixing = params['Mixing method']
    #coating_speed = params['Dip-coating speed (mm/min)']
    #spanning = params['Whole film spanning of BF?']
    
    #========= IMAGE PROCESSING =============================
    
    
    #SEM-info bar is cropped by calling the written function
    #Information on what to input is included in the section where the 
    #function is defined (All functions are defined in the beginning of the
    #script, in the region before main():)
    pores = crop_bottom(image, 770, visualize = True)
    plt.axis('off')
    
    #If noise removal is to be done, the next line should be commented in.
    pores = remove_noise(pores, visualize = False)
    plt.axis('off')
    
    #Next line can be used to add or decrease contrast. 
    contrasted = contrast(pores, 2, visualize = True)
    plt.axis('off')
    
    #Thresholding to get the binary image
    #Depending on which line is commented in, thresholding can be done
    #with either a filter or a handpicked value. 
    binary = threshold_filter(contrasted, 'mean', visualize = True)
    #binary = threshold_handpicked(contrasted, 10, visualize = True)
    
    #=========== IMAGE PROCESSING ENDS ==============================
    
    #=========== MEASURING OF PORE AREAS =============================
    #NO CHANGES REQUIRED IN THIS SECTION
    
    #important step for watershed function, measures distance to the background map.
    distance = ndi.distance_transform_edt(binary) 
    #plt.imshow(exposure.adjust_gamma(distance, 0.5))
    #plt.title('Distance to background map')

    #detects the center of each pore
    local_maxima = morphology.local_maxima(distance) 
    
    #plots the original image & detected centers (local maximas)
    fig, ax = plt.subplots(figsize=(20,20))
    maxi_coords = np.nonzero(local_maxima)
    ax.imshow(pores)
    #plt.title('Detected pore centers')
    plt.scatter(maxi_coords[1], maxi_coords[0])
    plt.axis('off')
    
    #each local maxima is considered to correspond to a pore
    markers = ndi.label(local_maxima)[0]
    
    #segmentation or determining pore outlines done with the watershed function
    labels_masked = segmentation.watershed(binary, markers, mask=binary, connectivity=5)

    
    #plots the original image & detected pore outlines
    f, ax1 = plt.subplots(figsize=(20,20))
    
    #ax0.imshow(binary)
    #ax0.imshow(pores)
    ax1.imshow(shuffle_labels(labels_masked), cmap='magma')
    contours = measure.find_contours(labels_masked, level = 2)
    plt.imshow(pores)
    for c in contours:
        plt.plot(c[:,1],c[:,0])

    regions = measure.regionprops(labels_masked)
    plt.axis('off')
    
    #2 lines below plot a histrogram of the distribution
    #f, ax = plt.subplots(figsize=(10,5))
    #ax.hist([r.area for r in regions], bins=5000)
    
    
    #========= MEASURING OF PORE AREAS ENDS ================================
    diameter = []
    #========= WRITING OUTPUT =========================================
    #Measured areas written to given output_file
   
    
    for r in regions:
        area = r.area/(nm_to_pixel**2)
        radius = np.sqrt(area/np.pi)
        diameter.append(radius*2)
    #output_file.write(str(sample) + ',' + str(diameter) + ',' + str(radius) + '\n')    
    #output_file.close()
    
    print(statistics.mean(diameter))
    print(statistics.stdev(diameter))
    f, ax = plt.subplots(figsize=(10,5))
    plt.hist([diameter], bins=500)
    plt.xlim(xmin=0, xmax = 2500)
    
            
    with open('return.csv','w') as f:
        writer = csv.writer(f)
        writer.writerows(zip(diameter))        
    
if __name__=="__main__":
    main()
