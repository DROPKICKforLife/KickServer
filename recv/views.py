from django.shortcuts import render
from django.http import HttpResponse
from .models import UserAccounts
from .models import UploadDatas
from .models import DoctorAccounts
import base64
import json
import io
import os
import configparser
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import boto
def index(request):
    def uploadIMG(filename):
        # if not boto.config.get('s3', 'use-sigv4'):
        #     boto.config.add_section('s3')
        #     boto.config.set('s3', 'use-sigv4', 'True')
        #
        #     pass

        config = configparser.ConfigParser()
        config.read('conf.ini')
        AccKey = config['AWSKeys']['AccessKey']
        PriKey = config['AWSKeys']['PrivateKey']
        Region = config['AWSKeys']['Region']
        print("connect start")
        #conn = boto.connect_s3(AccKey,PriKey)

        # conn = S3Connection(aws_access_key_id=AccKey,aws_secret_access_key=PriKey)
        conn = boto.s3.connect_to_region(Region, aws_access_key_id=AccKey, aws_secret_access_key=PriKey,is_secure=False)

        print("get bucket")
        #bucketName = config['AWSKeys']['BucketName']
        #bucket = conn.get_bucket(bucket_name=bucketName)
        bucket = conn.get_all_buckets()[0]
        print(bucket)
        # key = Key(bucket)
        key = bucket.new_key(filename)
        key.key = filename
        key.set_contents_from_filename(filename)
        key.set_acl('public-read')
        print("업로드 완료")
        os.remove(filename)
        print("임시파일 삭제완료")
        print("이미지데이터 30일 보관 설정중")
        return key.generate_url(3600 * 24 * 30)  # 30일 보관
    def loadIMG(imgdata):
        try:
            filename = imgdata['userid']+"_"+imgdata['identify']+'.png'
            print(filename)
            splitData = str(imgdata['imgdata']).split(',')[1]
            decodeData = base64.b64decode(splitData.encode('ascii'))
            file = io.open(filename,mode='wb')
            file.write(decodeData)
            file.close()
            print("이미지파일 생성완료")
        except(Exception):
            print("ERROR")
            return "ERR"
        finally:
            return filename
    def addUserAcount(userid,userpw,phone,sex):
        query = UserAccounts.objects.create(
            userID=userid,
            userPW=userpw,
            phone=phone,
            sex=sex
        )
        query.save()
        for i in UserAccounts.objects.all():
            print(i.id)
            print(i.userID)
            print(i.phone)
            pass
        pass
    def uploadSQL(userid,treeurl,houseurl):
        try:
            query = UploadDatas.objects.create(
                userID=userid,
                treeURL = treeurl,
                houseURL = houseurl
            )
            query.save()
            for i in UploadDatas.objects.all():
                print(i.id)
                print(i.userID)
                print(i.treeURL)
                print(i.houseURL)
                print(i.lastEdit)
                # print(i.id +" " +i.userID + " "+i.treeURL + " "+ i.houseURL +" "+ i.lastEdit)
        except:
            print("SQL ERROR")
            pass
        finally:
            print("upload SUCCESS")
        pass

    if request.method == "POST":
        print("POST recv")
        postdata = request.POST.dict()
        print(postdata)
        if 'identify' in postdata and 'userid' in postdata and 'imgdata' in postdata:
        # if postdata['userid'] and postdata['identify'] and postdata['imgdata']:
            filename = loadIMG(postdata)
            print(filename)
            url = str(uploadIMG(filename)).split('?')[0]
            data = {
                'result' : {
                    'message' : 'success',
                    'imgurl' : url
                }
            }
        else:
            data = {
                'result':{
                    'message':'upload_error'
                }
            }
            pass
        uploadSQL(postdata['userid'],url,url)
        return HttpResponse(json.dumps(data))
    else:
        print("GET!")

        return HttpResponse("HI")
    pass
