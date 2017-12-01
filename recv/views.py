from django.shortcuts import render
from django.http import HttpResponse
from .models import UserAccounts
from .models import UploadDatas
from .models import DoctorAccounts
from .models import Weeks
import base64
import json
import io
import os
import configparser
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import boto
import datetime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings


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
    # conn = boto.connect_s3(AccKey,PriKey)

    # conn = S3Connection(aws_access_key_id=AccKey,aws_secret_access_key=PriKey)
    conn = boto.s3.connect_to_region(Region, aws_access_key_id=AccKey, aws_secret_access_key=PriKey, is_secure=False)

    print("get bucket")
    # bucketName = config['AWSKeys']['BucketName']
    # bucket = conn.get_bucket(bucket_name=bucketName)
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
def index(request):

    def loadIMG(imgdata,filedata):
        try:
            filename = imgdata['userid']+"_"+imgdata['identify']+str(datetime.datetime.now().timestamp())+'.png'
            print(filename)
            # path = default_storage.save(filename,ContentFile(filedata.read()))
            # print("path 설정 완료")
            # tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            file = io.open(filename, mode='wb')
            file.write(filedata.read())
            # splitData = str(filedata).split(',')[1]
            # decodeData = base64.b64decode(splitData.encode('ascii'))
            # file = io.open(filename,mode='wb')
            # file.write(decodeData)
            file.close()
            print("이미지파일 생성완료")
        except(Exception):
            print("ERROR")
            return "ERR"
        finally:
            return filename

    def uploadSQL(userid,dataurl):
        try:
            query = UploadDatas.objects.create(
                userID=userid,
                dataurl = dataurl
            )
            query.save()
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
        filedata = request.FILES
        for i in filedata:
            filevalue = filedata[i]
            break
        print(filevalue)
        if 'identify' in postdata.keys() and 'userid' in postdata.keys():
            # if postdata['userid'] and postdata['identify'] and postdata['imgdata']:
            filename = loadIMG(postdata,filevalue)
            print(filename)
            url = str(uploadIMG(filename)).split('?')[0]
            data = {
                    'result' : {
                        'message' : 'success',
                        'imgurl' : url
                    }
            }
            uploadSQL(postdata['userid'],url,url)
        else:
            data = {
                    'result':{
                        'message':'upload_error'
                    }
            }
            pass
        return HttpResponse(json.dumps(data))
    else:
        print("GET!")

        return HttpResponse("HI")
    pass
from django.shortcuts import redirect
def upload(request):
    if request.method == "POST":
        postdata = request.POST.dict()
        userid = postdata['userid']
        imgdata = postdata['file']
        if postdata['root'] == 'root':
            filename = 'root_'+str(datetime.datetime.now().timestamp())+'.png'
        elif postdata['root'] == 'noroot':
            filename = 'noroot_'+str(datetime.datetime.now().timestamp())+'.png'
        file = io.open(filename, mode='wb')

        splitData = str(imgdata).split(',')[1]
        decodeData = base64.b64decode(splitData.encode('ascii'))
        file.write(decodeData)
        file.close()
        url = uploadIMG(filename).split('?')[0]
        return redirect(url)
        # return HttpResponse(url)

def addUserAcount(usertoken,childname,childsex,childbirth,childability,prevcontent,hopecontent:None):
    time = datetime.datetime.fromtimestamp(float(childbirth))
    if hopecontent != None:
        query = UserAccounts.objects.create(
            usertoken = usertoken,
            childname = childname,
            childsex = int(childsex),
            childbirth = time,
            childability = int(childability),
            prevcontent = prevcontent,
            hopecontent = hopecontent
        )
    else:
        query = UserAccounts.objects.create(
            usertoken = usertoken,
            childname=childname,
            childsex=int(childsex),
            childbirth=time,
            childability=int(childability),
            prevcontent=prevcontent
        )
    query.save()
    for i in UserAccounts.objects.all():
        print(i.userid)
        pass
    pass
def useradd(request): # 유저등록
    if request.method == "POST":
        postdata = request.POST.dict()
        if ('usertoken' not in postdata):
            result = {
                "result": "invalid token.."
            }
        elif 'childname' in postdata and 'childsex' in postdata and 'childbirth' in postdata and 'childability' in postdata and 'prevcontent' in postdata:

            if 'hopecontent' in postdata:
                addUserAcount(childname=postdata['childname'],childsex=postdata['childsex'],childbirth = postdata['childbirth'],childability=postdata['childability'],prevcontent=postdata['prevcontent'],hopecontent=postdata['hopecontent'])
            else:
                addUserAcount(childname=postdata['childname'],childsex= postdata['childsex'],childbirth = postdata['childbirth'],childability= postdata['childability'],prevcontent = postdata['prevcontent'],hopecontent=None)
            result = {
                "result":"success"
            }
        else:
            result = {
                "result": "ERR"
            }
    else:
        result = {
            "result":"Do not INPUT GET"
        }
        print(datetime.datetime.now().timestamp())
    return HttpResponse(json.dumps(result))
def usercheck(request):
    if request.method == "POST":
        postdata = request.POST.dict()
        if 'usertoken' in postdata:
            token = postdata['usertoken']
            try:
                if token in UserAccounts.objects.all().usertoken:
                    result = {
                        'result':'exist'
                    }
            except:
                result = {
                    'result':'null'
                }
        else:
            result = {
                'result':'err'
            }
    else:
        getdata = request.GET.dict()
        if 'usertoken' in getdata:
            token = getdata['usertoken']
            try:
                if token in UserAccounts.objects.all().usertoken:
                    result={
                        'result':'exist'
                    }
            except:
                result={
                    'result' :'null'
                }
        else:
            result={
                'result':'err'
            }

    return HttpResponse(json.dumps(result))

def viewdoctor(request):
    if request.method == "GET":
            result = []
            for i in DoctorAccounts.objects.all():
                result.append({
                       'doctorcount' : i.doctorcount,
                       'doctorname' : i.doctorname,
                       'hospitalname' : i.hospitalname,
                       'profileimgurl' : i.profileimgurl,
                       'speclist' : i.speclist,
                       'schoolname' : i.schoolname
                       })

            returndata = {
                   'result': result
            }
            return HttpResponse(json.dumps(returndata))

    return  HttpResponse("please GET data")

def viewweek(request):
    if request.method == "GET":
        getdata = request.GET.dict()
        if 'weekid' in getdata:
            weekid = getdata['weekid']
            result = {
                'result' : 'out of index'
            }
            for i in Weeks.objects.all():
                if weekid == i.weekid:
                    result = {
                        'weekcontents' : i.weekcontents

                    }
                    break
                    pass
            return json.dumps(result)
        return "Please parameter 'weekid'"
    return "please GET data"
# -*-coding:utf-8-*-