from qiniu import Auth, put_file, etag
import qiniu.config


def getQiniuUploadToken():
    # 需要填写你的 Access Key 和 Secret Key
    access_key = 'XU9381o-j2I9LLG8xPezpKTRiKPTu0uFFEbDNz4W'
    secret_key = 'Z1mlEjsPLwzPd01y_fRt-cn26y0vwrdE60k_593y'
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'moyusoldier'
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, expires=3600)
    return token
