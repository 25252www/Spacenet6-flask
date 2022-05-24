#!/usr/bin/env python
import os
import glob
import numpy as np
import skimage
import gdal
import solaris as sol
import model_efficientnet


# Custom model dictionaries, defined globally
sar_dict = {
    'model_name': 'unet_efficientnet_b5',
    'weight_path': None,
    'weight_url': None,
    'arch': model_efficientnet.unet_efficientnet_b5
}


def test():
    """
    Uses the trained model to conduct inference on the test dataset.
    Outputs are a continuously-varying pixel map, a binary pixel map,
    and a CSV file of vector labels for evaluation.
    """
    print('Test')

    # Run inference on the test data
    config = sol.utils.config.parse('./sar.yaml')
    inferer = sol.nets.infer.Inferer(config, custom_model_dict=sar_dict)
    print('Start inference.')
    inferer()
    print('Finished inference.')

    # Binary and vector inference output
    driver = gdal.GetDriverByName('GTiff')
    sourcefolder = os.path.abspath(config['inference']['output_dir'])
    sourcefiles = sorted(glob.glob(os.path.join(sourcefolder, '*')))
    minbuildingsize = float(80)
    for sourcefile in sourcefiles:
        filename = os.path.basename(sourcefile)
        destfile = os.path.join(os.path.abspath(
            './inference_binary'), filename)

        # Create binary array
        cutoff = 0.
        sourcedataorig = gdal.Open(sourcefile).ReadAsArray()
        sourcedata = np.zeros(np.shape(sourcedataorig), dtype='int')
        sourcedata[np.where(sourcedataorig > cutoff)] = 255
        sourcedata[np.where(sourcedataorig <= cutoff)] = 0

        # Remove small buildings
        if minbuildingsize > 0:
            regionlabels, regioncount = skimage.measure.label(
                sourcedata, background=0, connectivity=1, return_num=True)
            regionproperties = skimage.measure.regionprops(regionlabels)
            for bl in range(regioncount):
                if regionproperties[bl].area < minbuildingsize:
                    sourcedata[regionlabels == bl+1] = 0

        # Save binary image
        destdata = driver.Create(
            destfile, sourcedata.shape[1], sourcedata.shape[0], 1, gdal.GDT_Byte)
        destdata.GetRasterBand(1).WriteArray(sourcedata)
        del destdata
