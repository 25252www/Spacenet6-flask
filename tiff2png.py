import os
import gdal
import numpy as np

def translateTiff32to8bit(inputPath, outputPath):
    # 32bit SAR 四通道 转为 8bit tiff RGB
    sarimg = gdal.Open(inputPath)
    sarimg = sarimg.ReadAsArray()  # (4,900,900)
    sarimg = sarimg[:3, :, :]
    # print(sarimg.dtype)
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(
        outputPath, sarimg.shape[2], sarimg.shape[1], sarimg.shape[0], gdal.GDT_Byte)
    for i, image in enumerate(sarimg, 1):  # 下标从 1 开始
        # 百分比截断
        image[image == 0] = np.nan
        cutmin = np.nanpercentile(image, 0.5)
        cutmax = np.nanpercentile(image, 99.5)
        # print('cutmin',cutmin,np.min(image))
        # print('cutmax',cutmax,np.max(image))
        image = np.clip(image, cutmin, cutmax)
        image = np.around((image - cutmin) * 255/(cutmax - cutmin))
        image[np.isnan(image)] = 0
        # print('min',np.min(image))
        # print('max',np.max(image))
        dataset.GetRasterBand(i).WriteArray(image)
    del dataset


def translateTiff2PNG(inputPath, outputPath):
    options = gdal.TranslateOptions(format='PNG')
    gdal.Translate(outputPath, inputPath, options=options)
    os.remove(inputPath)


def translatebefore(inputPath, outputPath):
    translateTiff32to8bit(inputPath, 'output.tiff')
    translateTiff2PNG('output.tiff', outputPath)


def translateafter(inputPath, outputPath):
    options = gdal.TranslateOptions(format='PNG')
    gdal.Translate(outputPath, inputPath, options=options)

