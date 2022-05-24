import os
import time
import requests
import pandas as pd
import baseline
import tiff2png
from qiniu import put_file
from common.lang.Result import Result
from common.lang import oss
from flask import Flask

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False


@app.route('/getQiniuUploadToken')
def getQiniuUploadToken():
    return Result.succ(oss.getQiniuUploadToken())


@app.route('/hello')
def hello_world():
    return Result.succ('Hello World!')


@app.route('/doSegmentation', methods=['POST'])
def doSegmentation():
    with app.app_context():
        # 下载图片并保存
        # requestBody = json.loads(request.get_data(as_text=True))
        # inputImgUrl = requestBody['inputImgUrl']
        inputImgUrl = 'https://cdn.moyusoldier.cn/inputImg_1653361993_SN6_Train_AOI_11_Rotterdam_SAR-Intensity_20190823135139_20190823135448_tile_1432.tif'
        inputImg = requests.get(inputImgUrl).content
        ImgBaseName = (inputImgUrl.split('/')[-1])[9:]
        ImgPath = os.path.join(os.path.abspath(
            './sartrain/'), ImgBaseName)
        with open(ImgPath, 'wb') as f:
            f.write(inputImg)
            print("saved")

        # 生成csv文件
        df = pd.DataFrame(columns=['image'])
        df = df.append({'image': ImgPath}, ignore_index=True)
        df.to_csv('test.csv', index=False)

        # 推理
        baseline.test()

        # 生成PNG图像
        outputImgSARPath = os.path.join(os.path.abspath(
            './outputImgSAR'), os.path.splitext(ImgBaseName)[0]+'.png')
        outputImgBinaryPath = os.path.join(os.path.abspath(
            './outputImgBinary'), os.path.splitext(ImgBaseName)[0]+'.png')
        tiff2png.translatebefore(ImgPath, outputImgSARPath)
        tiff2png.translateafter(os.path.join(os.path.abspath(
            './inference_binary'), os.path.basename(ImgPath)), outputImgBinaryPath)

        # 上传到七牛云
        token = oss.getQiniuUploadToken()
        outputImgSARKey = 'outputImgSAR_' + \
            str(int(time.time())) + '_' + ImgBaseName
        outputImgBinaryKey = 'outputImgBinary_' + \
            str(int(time.time())) + '_' + ImgBaseName
        res1, info = put_file(token, outputImgSARKey,
                              outputImgSARPath, version='v2')
        res2, info = put_file(token, outputImgBinaryKey,
                              outputImgBinaryPath, version='v2')
        outputImgSARUrl = "https://cdn.moyusoldier.cn/" + res1['key']
        outputImgBinaryUrl = "https://cdn.moyusoldier.cn/" + res2['key']
        responseData = {'outputImgSARUrl': outputImgSARUrl,
                        'outputImgBinaryUrl': outputImgBinaryUrl}

        # 删除本地图片
        os.remove(ImgPath)
        os.remove(os.path.join(os.path.abspath(
            './inference_continuous'), ImgBaseName))
        os.remove(os.path.join(os.path.abspath(
            './inference_binary'), ImgBaseName))
        os.remove(outputImgSARPath)
        os.remove(outputImgBinaryPath)

        return Result.succ(responseData)


if __name__ == '__main__':
    # app.run()
    doSegmentation()
