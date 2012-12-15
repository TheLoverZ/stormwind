# -*- coding: UTF-8 -*-

import config
import rs
import uptoken
import rscli
import digestoauth

APP_NAME = 'uplist'

class Qiniu():
    def __init__(self):
        config.ACCESS_KEY = 'Al0pafXaNnybHacKLGbN0IuH1Msl3xM8XokpUHDH'
        config.SECRET_KEY = 'SDIX2iH577oKo-Obq9-npNL4LGoPrgDuIMsZyqmR'
        tokenObj = uptoken.UploadToken(
            scope = APP_NAME,
            expires_in = 31536000, #one year
            )
        uploadtoken = tokenObj.generate_token()
        self.token = uploadtoken
        client = digestoauth.Client()
        bucket = APP_NAME
        self.rs = rs.Service(client, bucket)
    def QiniuUpload(self, bucket, key, mimeType, localFile):
        resp = rscli.UploadFile(
            bucket,
            key, 
            mimeType, 
            localFile, 
            upToken = self.token,
            )
        return resp
    def QiniuStat(self, key):
        resp = self.rs.Stat(key)
        return resp
    def QiniuDownload(self, key, destination):
        resp = self.rs.Get(key, attName=destination)
        return resp

if __name__ == '__main__':
    a = Qiniu()
    #upload
    bucket = APP_NAME
    key = "a unique name"
    mimeType = 'file type' #'image/jpg'
    localFile = "local file path"
    print a.QiniuUpload(bucket, key, mimeType, localFile)
    #file stat
    key = "file name"
    print a.QiniuStat(key)
    #download
    key = "file name"
    destination = "destination file name"
    print a.QiniuDownload(key, destination)['url']