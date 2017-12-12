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

config = configparser.ConfigParser()
config.read('conf.ini')
def uploadIMG(filename):
    # if not boto.config.get('s3', 'use-sigv4'):
    #     boto.config.add_section('s3')
    #     boto.config.set('s3', 'use-sigv4', 'True')
    #
    #     pass

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
from .tree_predict import predict_tree
from .house_predict import predict_house
def index(request):

    def loadIMG(imgdata,filedata):
        try:
            filename = imgdata['userid']+"_"+imgdata['identify']+str(datetime.datetime.now().timestamp())+'.png'
            file = io.open(filename, mode='wb')
            file.write(filedata.read())
            file.close()
        except(Exception):
            print("ERROR")
            return "ERR"
        finally:
            return filename

    def uploadSQL(userid,dataurl):
        try:
            print(userid)
            print(dataurl)
            content = predict(dataurl)
            print(content)
            query = UploadDatas.objects.create(
                userid=userid,
                dataurl = dataurl,
                content = content
            )
            query.save()
        except Exception as ex:
            print(ex)
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
            uploadSQL(postdata['userid'],url)
            if UserAccounts.objects.filter(usertoken=postdata['userid']).count() == 1:
                useracc = UserAccounts.objects.get(usertoken=postdata['userid'])
                useracc.week = 1
                useracc.save()
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

        return render(request, '404.html')
    pass
from django.shortcuts import redirect
def upload(request):
    if request.method == "POST":
        filedata = request.FILES.dict()

        imgdata = None
        for i in filedata:
            print(i)
            imgdata = i
        postdata = json.loads(request.body.decode('utf-8'))
        userid = postdata['userid']
        filename = postdata['identify']+"_"+ str(datetime.datetime.now().timestamp())+'.png'
        file = io.open(filename, mode='wb')

        splitData = str(imgdata).split(',')[1]
        decodeData = base64.b64decode(splitData.encode('ascii'))
        file.write(decodeData)
        file.close()
        url = uploadIMG(filename).split('?')[0]
        return redirect(url)
        # return HttpResponse(url)

def addUserAcount(usertoken,childname,childsex,childbirth,childability,prevcontent,hopecontent:None):
    time = datetime.datetime.fromtimestamp(float(childbirth)/1000)
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
    pass
def useradd(request): # 유저등록
    if request.method == "POST":
        postdata = json.loads(request.body.decode('utf-8'))
        print(postdata)
        if 'usertoken' in postdata:
            usertoken = postdata['usertoken']
            if UserAccounts.objects.filter(usertoken=usertoken).count() > 0:
                result = {
                    "result" : "success"
                }
                return HttpResponse(json.dumps(result))

        if 'usertoken' not in postdata:
            result = {
                "result": "invalid token.."
            }
        elif 'childname' in postdata and 'childsex' in postdata and 'childbirth' in postdata and 'childability' in postdata and 'prevcontent' in postdata:

            if 'hopecontent' in postdata:
                addUserAcount(usertoken=postdata['usertoken'] ,childname=postdata['childname'],childsex=postdata['childsex'],childbirth = postdata['childbirth'],childability=postdata['childability'],prevcontent=postdata['prevcontent'],hopecontent=postdata['hopecontent'])
            else:
                addUserAcount(usertoken=postdata['usertoken'] ,childname=postdata['childname'],childsex= postdata['childsex'],childbirth = postdata['childbirth'],childability= postdata['childability'],prevcontent = postdata['prevcontent'],hopecontent=None)
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
        postdata = json.loads(request.body.decode('utf-8'))
        # print(postdata)
        # postdata = postdata.dict()
        print(postdata)
        if 'usertoken' in postdata:
            token = postdata['usertoken']
            try:
                if UserAccounts.objects.filter(usertoken=token).count() > 0:
                    result = {
                        'result':'exist'
                    }
                else:
                    result = {
                    'result':'null'
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
                print(UserAccounts.objects.filter(usertoken=token).count())
                if UserAccounts.objects.filter(usertoken=token).count() > 0:
                    result={
                        'result':'exist'
                    }
                else:
                    result = {
                        'result': 'null'
                    }

            except:
                result={
                    'result' :'null'
                }
        else:
            result={
                'result':'err'
            }
    print(result)
    return HttpResponse(json.dumps(result))
import ast
def viewdoctor(request):
    if request.method == "GET":
            result = []
            for i in DoctorAccounts.objects.all():
                result.append({
                       'doctorcount' : i.doctorcount,
                       'doctorname' : i.doctorname,
                       'hospitalname' : i.hospitalname,
                       'profileimgurl' : i.profileimgurl,
                       'speclist' : ast.literal_eval(i.speclist),
                       'schoolname' : i.schoolname,
                        'doctor_id':i.doctorid
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
            return HttpResponse(json.dumps(result))
        return HttpResponse("Please parameter 'weekid'")
    return render(request,'404.html')
# def page(request):
#     return render(request,'index.html')
def kakaologin(request):
    REST = config['Kakao']['REST']

    url = "https://kauth.kakao.com/oauth/authorize?client_id=%s&redirect_uri=http://ec2-52-78-149-26.ap-northeast-2.compute.amazonaws.com/oauth&response_type=code"%REST


    return redirect(url)
    #
    # return HttpResponse("success")
from .models import DoctorAccounts
import requests as req
def kakaoOATH(code):
    grant_type = "authorization_code"
    client_id = config['Kakao']['REST']
    redirect_uri = "http://ec2-52-78-149-26.ap-northeast-2.compute.amazonaws.com/oauth"
    url = "https://kauth.kakao.com/oauth/token"
    data = {
                'grant_type': grant_type,
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'code': code
            }
    r = req.post(url, data=data)
    cont = r.text
    print(data)
    print(cont)
    cont = json.loads(cont)
    return cont
def getdrcode(request):
    if request.method == "GET":
        if 'code' in request.GET:
            code = request.GET['code']
            request.session['code'] = code
            cont = kakaoOATH(code=code)

            if 'access_token' not in cont:
                return gotoindex(request,context=None)
                # return render(request,'signin.html')
            access_token = cont['access_token']
            request.session['access_token'] = access_token
            token_type = cont['token_type']
            refresh_token = cont['refresh_token']
            expires_in = cont['expires_in']
            scope = cont['scope']
            url = "https://kapi.kakao.com/v1/user/signup"
            headers= {'Authorization':"{0} {1}".format(token_type,access_token)}
            answer =req.post(url,headers=headers)
            answer = json.loads(answer.text)
            print(answer)
            if 'id' in answer:
                result = answer['id']
                print(newdoctor(token_type, access_token))
            else:
                print(answer)
                result = answer['msg']
                kko = Kakaoaccount(token_type, access_token)
                alreadyconfig = logindoctor(kko)
                if alreadyconfig == True: #메인페이지로
                    acc = DoctorAccounts.objects.get(doctorid=kko.id)
                    if acc.confirm == True:
                        useracc = UserAccounts.objects.filter(doctorid=acc.doctorid)
                        request.session['doctorid'] = acc.doctorid

                        return redirect('/recv/login')
                        # return gotoindex(request, context={'acc' : acc,'useracc':useracc})

                        # return gotoindex(request,context={'doctorname':acc.doctorname,'profileimg':acc.profileimgurl})
                    else:
                        return HttpResponse("아직 관리자에게 승인되지 않은 상담사님 입니다. 관리자에게 문의해 주세요.")
                else:
                    return render(request,'signup.html',context={'kko' : kko})

                    # return render(request,'signup.html',context={'kaccount_email' : kko.kaccount_email,'doctorid' : kko.id})

            return HttpResponse(result)
        # req.urlopen(url,data={'grant_type' : grant_type, 'client_id': client_id, 'redirect_uri' : redirect_uri, 'code' : code })
    else:
        return render(request, '404.html')
class Kakaoaccount:
    def __init__(self,token_type,access_token):
        url = "https://kapi.kakao.com/v1/user/me"
        headers = {'Authorization': "{0} {1}".format(token_type, access_token)}
        answer = req.post(url=url, data=None, headers=headers)
        answer = json.loads(answer.text)
        self.kaccount_email = answer['kaccount_email']
        self.kaccount_email_verified = answer['kaccount_email_verified']
        self.id = answer['id']
        data = answer['properties']
        self.thumbnail_image = data['thumbnail_image']
        self.nickname = data['nickname']
        self.profile_image = data['profile_image']
def logindoctor(kko):
    for i in DoctorAccounts.objects.all():
        if i.doctorid == kko.id:
            return(True)
    print("noname") #초기 설정 페이지로 이동
    return(False)
def newdoctor(token_type,access_token):
    url = "https://kapi.kakao.com/v1/user/me"
    headers= {'Authorization':"{0} {1}".format(token_type,access_token)}
    answer = req.post(url=url,data=None,headers=headers)
    answer = json.loads(answer.text)
    kaccount_email = answer['kaccount_email']
    kaccount_email_verified = answer['kaccount_email_verified']
    id = answer['id']
    data = answer['properties']
    thumbnail_image = data['thumbnail_image']
    nickname= data['nickname']
    profile_image = data['profile_image']
    for i in DoctorAccounts.objects.all():
        if i.doctorid == id:
            return "already registered!"
    DoctorAccounts.objects.create(
        doctorid = id,
        doctorkakaoid = kaccount_email,
        profileimgurl = profile_image
    ).save()

    print(kaccount_email)
    return "success"
def loginpage(request):
    cont = None
    if 'doctorid' in request.session:
        doctorid = request.session['doctorid']
        doctoracc = DoctorAccounts.objects.get(doctorid=doctorid)
        childacc = UserAccounts.objects.filter(doctorid=doctorid)
        reqcount = 0
        commentcount = 0
        reqname = []
        for i in childacc:
            imgdata = UploadDatas.objects.filter(userid=i.usertoken)
            for j in imgdata:
                if j.dataurl.find('tree'):
                    reqcount = 1
                    if Week1.objects.filter(childid=i.usertoken,doctorid=doctorid,sender=False).count() > 0:
                        break

                    reqname.append({
                        'childid' : i.usertoken,
                        'childname': i.childname,
                        'childsex' : i.childsex
                    })
                    break
                elif j.dataurl.find('house'):
                    reqcount = 1
                    if Week1.objects.filter(childid=i.usertoken,doctorid=doctorid,sender=False).count() > 0:
                        break
                    reqname.append({
                        'childid' : i.usertoken,
                        'childname': i.childname,
                        'childsex' : i.childsex})
                    break

                elif j.dataurl.find('person'):
                    reqcount = 1
                    if Week1.objects.filter(childid=i.usertoken,doctorid=doctorid,sender=False).count() > 0:
                        break
                    reqname.append({
                        'childid' : i.usertoken,
                        'childname': i.childname,
                        'childsex' : i.childsex})
                    break
        childarr = []
        commentcontents = []
        for i in Week1.objects.filter(doctorid=doctorid,sender=False):
            if i.childid in childarr:
                continue
            else:
                childarr.append(i.childid)
                useracc = UserAccounts.objects.get(usertoken=i.childid)
                childname = useracc.childname
                childsex = useracc.childsex
                commentcontents.append({
                    'userid' : i.childid,
                    'childsex' : childsex,
                    'childname' : childname,
                    'content' : i.content.replace('\\n',' ')
                })
                commentcount +=1
        print("######")
        print(reqcount)
        # reqcount = reqcount - commentcount
        # reqcount += Week1.objects.filter(doctorid=doctorid, sender=True).count()
        # commentcount = Week1.objects.filter(doctorid=doctorid, sender=False).count()
        return gotoindex(request,context={'acc' : doctoracc,'useracc':childacc,'reqcount':reqcount,'commentcount':commentcount,'commentcontents':commentcontents,'reqname':reqname})

    return gotoindex(request,context=cont)
    # return render(request,'signin.html')

def savedoctorconfig(request):
    if request.method == "POST":
        postdata = request.POST.dict()
        print(postdata)

        if 'doctorname' in postdata and 'doctorphone' in postdata and 'doctorschool' in postdata and 'doctoremail' in postdata and 'hospitalname' in postdata:

            acc = None
            for i in DoctorAccounts.objects.all():
                if i.doctorid == postdata['doctorid']:
                    acc =i
                # else:
                #     DoctorAccounts.objects.create(
                #         doctorid = postdata['doctorid']
                #     ).save()
                #     acc =DoctorAccounts.objects.get(doctorid=postdata['doctorid'])
            if acc == None:
                DoctorAccounts.objects.create(
                    doctorid=postdata['doctorid'],
                    profileimgurl = postdata['profile_image']
                ).save()
                acc = DoctorAccounts.objects.get(doctorid=postdata['doctorid'])
            acc.doctorname = postdata['doctorname']
            acc.doctorphone = postdata['doctorphone']
            acc.schoolname = postdata['doctorschool']
            acc.doctoremail = postdata['doctoremail']
            acc.hospitalname = postdata['hospitalname']
            acc.speclist = str(postdata['doctor_spec'].strip().split(','))
            acc.save()
            return HttpResponse("아직 관리자에게 승인되지 않은 상담사님 입니다. 관리자에게 문의해 주세요.")
            # return render(request,'index.html',context={'doctorname':postdata['doctorname'],'profileimg':acc.profileimgurl})

        return HttpResponse(postdata)
    else:
        return render(request, '404.html')

def confirm_doctor(request):
    if request.method == "POST":
        postdata = request.POST.dict()
        print(postdata)
        if'doctorid' in postdata:
            id = postdata['doctorid']
            acc = DoctorAccounts.objects.get(doctorid=id)
            if acc.confirm == False:
                acc.confirm = True
                acc.save()
                return HttpResponse("Now, Confirm is True")
            else:
                acc.confirm = False
                acc.save()
                return HttpResponse("Now, Confirm is False")
        render(request, '404.html')
def gotoindex(request,context:None):
    if context == None:
        return render(request,'signin.html')
    else:
        return render(request,'index.html',context=context)
from .models import Week1
from .models import Week2
from .models import Week3
from .models import Week4
def childpage(request):
    if request.method =="GET":
        getdata = request.GET.dict()
        if 'id' in getdata:
            userid = getdata['id']
            try:
                doctorid = request.session.get('doctorid')
                doctoracc = DoctorAccounts.objects.get(doctorid=doctorid)
                print('1')
                print(userid)
                childacc = UserAccounts.objects.get(usertoken=userid)
                print('1.5')
                dt = datetime.datetime.today().year
                delta = dt - childacc.childbirth.year
                childacc.childage = delta
                week1 = None
                imgdatas =UploadDatas.objects.filter(userid=childacc.usertoken)
                houseurl = None
                treeurl = None
                personurl = None
                uploadtime = None
                treecontent =None
                housecontent = None
                personcontent = None
                #상담요청
                reqcount = 0
                #답변완료
                commentcount = None
                for i in imgdatas:

                    if i.dataurl.find('tree') > -1:
                        treeurl = i.dataurl
                        uploadtime = i.uploadtime
                        treecontent =i.content.replace('\n','<br />')
                        reqcount = 1
                    elif i.dataurl.find('house') > -1:
                        houseurl = i.dataurl
                        uploadtime = i.uploadtime
                        housecontent =i.content.replace('\n','<br />')
                        reqcount = 1
                    elif i.dataurl.find('person') > -1:
                        personurl = i.dataurl
                        uploadtime = i.uploadtime
                        personcontent =i.content.replace('\n','<br />')
                        reqcount = 1
                week1 = None
                if Week1.objects.filter(childid=childacc.usertoken).count() > 0:
                    print(Week1.objects.count())
                    week1 = Week1.objects.filter(doctorid=doctorid,childid=childacc.usertoken)
                    print("3")
                    for i in week1:
                        i.content = i.content.replace('\\n','<br/>')
                    # reqcount += Week1.objects.filter(doctorid=doctorid,childid=childacc.usertoken,sender=True).count()
                    commentcount = Week1.objects.filter(doctorid=doctorid,childid=childacc.usertoken,sender=False).count()
                useracc = UserAccounts.objects.filter(doctorid=doctorid)
                print('4')
                prevcontent = Week1.objects.filter(doctorid=doctorid,childid=childacc.usertoken)

                print('5')
                week2 = None
                week3 = None
                week4 = None
                week2_communication = None
                week3_communication = None
                week4_communication = None
                if Weeks.objects.filter(weekid=2) is not None:
                    week2 = Weeks.objects.filter(weekid=2)
                if Weeks.objects.filter(weekid=3) is not None:
                    week3 = Weeks.objects.filter(weekid=3)
                if Weeks.objects.filter(weekid=4) is not None:
                    week4 = Weeks.objects.filter(weekid=4)
                week2_communication =Week2.objects.filter(childid=userid,doctorid=doctorid,sender=True)


                week2_count = week2_communication.count()
                print("5.5")
                if week2_count > 0:
                    week2_communication = Week2.objects.get(childid=userid,doctorid=doctorid,sender=True)

                    for i in week2_communication:
                        i.content = i.content.replace('\\n','<br/>')
                week3_communication = Week3.objects.filter(childid=userid, doctorid=doctorid, sender=True)
                week3_count = week3_communication.count()
                if week3_count > 0:
                    week3_communication = Week3.objects.get(childid=userid, doctorid=doctorid, sender=True)

                    for i in week3_communication:
                        i.content = i.content.replace('\\n','<br/>')
                week4_communication = Week4.objects.filter(childid=userid, doctorid=doctorid, sender=True)
                week4_count = week4_communication.count()
                if week4_count > 0:
                    week4_communication = Week4.objects.get(childid=userid, doctorid=doctorid, sender=True)
                    print('6')
                    for i in week4_communication:
                        i.content = i.content.replace('\\n','<br/>')
                print(week1)

                return render(request, 'childpage.html', context={'week4_count':week4_count,'week4':week4,'week4_communication':week4_communication,'week3_count':week3_count,'week3':week3,'week3_communication':week3_communication,'week2_count':week2_count,'useracc':useracc,'childacc': childacc, 'doctoracc': doctoracc,'week1':week1,'houseurl':houseurl,'treeurl':treeurl,'personurl':personurl,'uploadtime':uploadtime,'treecontent':treecontent,'housecontent':housecontent,'personcontent':personcontent,'reqcount':reqcount,'commentcount':commentcount,'prevcontent':prevcontent,'week2':week2,'week2_communication':week2_communication})
                    # return HttpResponse(childacc)# 환자 페이지로 값을 넘길것
            except Exception as ex:
                print(ex)
                return render(request,'404.html')
    return render(request, '404.html')
def sendmessage(request):
    postdata = request.POST.dict()
    week_index = int(postdata['week_id'])
    request_type =  False
    if postdata['request_type'] == "reply_reply":
        request_type = True
    if week_index == 1:
        Week1.objects.create(
            doctorid = postdata['doctorid'],
            childid = postdata['childid'],
            sender = False,
            content = postdata['content'].replace('\r\n','\\n'),
            request_type = request_type
        ).save()
    elif week_index == 2:
        Week2.objects.create(
            doctorid=postdata['doctorid'],
            childid=postdata['childid'],
            sender=False,
            content = postdata['content'].replace('\r\n','\\n'),
            request_type=request_type
        ).save()
    elif week_index == 3:
        Week3.objects.create(
            doctorid=postdata['doctorid'],
            childid=postdata['childid'],
            sender=False,
            content = postdata['content'].replace('\r\n','\\n'),
            request_type=request_type
        ).save()
    elif week_index == 4:
        Week4.objects.create(
            doctorid=postdata['doctorid'],
            childid=postdata['childid'],
            sender=False,
            content = postdata['content'].replace('\r\n','\\n'),
            request_type=request_type
        ).save()

    print(postdata)
    return HttpResponse("<script>location.replace('/recv/childpage?id="+postdata['childid']+"')</script>")
def sendcontent(request):
    if request.method =="POST":
        postdata = json.loads(request.body.decode('utf-8'))
        if 'doctor_id' in postdata and 'child_id' in postdata and 'sender' in postdata and 'content' in postdata and 'week_id' in postdata:
            week_index = int(postdata['week_id'])
            if week_index == 1:
                Week1.objects.create(
                    doctorid=postdata['doctor_id'],
                    childid=postdata['child_id'],
                    sender=False,
                    content=postdata['content'],
                    request_type = False
                ).save()
            elif week_index == 2:
                Week2.objects.create(
                    doctorid=postdata['doctor_id'],
                    childid=postdata['child_id'],
                    sender=False,
                    content=postdata['content'],
                    request_type=False
                ).save()
            elif week_index == 3:
                Week3.objects.create(
                    doctorid=postdata['doctor_id'],
                    childid=postdata['child_id'],
                    sender=False,
                    content=postdata['content'],
                    request_type=False
                ).save()
            elif week_index == 4:
                Week4.objects.create(
                    doctorid=postdata['doctor_id'],
                    childid=postdata['child_id'],
                    sender=False,
                    content=postdata['content'],
                    request_type=False
                ).save()
            return json.dumps({
                'result' : 'success'
            })
    return json.dumps({
        'result' : 'err'
    })
def viewcontents(request):
    if request.method == "GET":
        getdata = request.GET.dict()
        if 'child_id' in getdata:
            objs = Week1.objects.filter(childid=getdata['child_id'])
            contents = []
            for i in objs:
                docacc = DoctorAccounts.objects.get(doctorid=i.doctorid)

                contents.append({
                    'doctor_name' : docacc.doctorname,
                    'content': [i.content],
                    'date' : i.date.timestamp(),
                    'request_type' : i.request_type
                })
            result = json.dumps({
                'result' : contents
            })
    else:
        result = json.dumps({
            'result' : "err"
        })
    return HttpResponse(result)
def testurl(request):
    postdata = request.POST.dict()
    print(postdata.items())
    return HttpResponse(postdata.items())

def predict(url):
    result =""
    if url.find('tree') > -1:
        result = predict_tree(url)
    elif url.find('house') >-1:
        result = predict_house(url)

    elif url.find('person') > -1:
        result = "감지된 특이점이 없습니다."
    return result
def getnowweek(request):
    result = None
    if request.method == "GET":
        getdata = request.GET.dict()
        print(getdata)
        if 'childid' in getdata:
            childid = getdata['childid']
            useracc = UserAccounts.objects.get(usertoken=childid)
            week = useracc.week
            result = {
                'result' : week
            }
    else:
        result = {
            'result' : 'err'
        }
    return HttpResponse(json.dumps(result))
def setnowweek(request):
    result = None
    if request.method == "POST":
        postdata = json.loads(request.body.decode('utf-8'))
        if 'childid' in postdata and 'week' in postdata:
            childid = postdata['childid']
            week = postdata['week']
            if UserAccounts.objects.filter(childid=childid).count() == 1:
                useracc = UserAccounts.objects.get(childid=childid)
                useracc.week = week
                useracc.save()
                result = {
                    'result' : 'success'
                }
    if result == None:
        result = {
            'result' : 'err'
        }
    return HttpResponse(json.dumps(result))

def getallweeks(request):
    if request.method == "GET":
        weeks = Weeks.objects.all()
        weekarr = []
        for i in weeks:
            weekarr.append(i.week_topic)
        result = {
            'result' : weekarr
        }
    else:
        result = {
            'result' : 'err'
        }
    return HttpResponse(json.dumps(result))

def connect_doctor(request):
    if request.method == "POST":
        # postdata = request.POST.dict()
        postdata = json.loads(request.body.decode('utf-8'))
        print(postdata)
        if 'userid' in postdata and 'doctorid' in postdata:
            useracc = UserAccounts.objects.get(usertoken=int(postdata['userid']))
            print("1@")
            useracc.doctorid = postdata['doctorid']
            print("2@")
            useracc.save()
            return HttpResponse(json.dumps({
                'result' : 'success'
            }))
    return HttpResponse(json.dumps({
        'result' : 'err'
    }))
def logout(request):
    if request.method == "GET":
        if 'code' in request.session:
            access_token = request.session.get('access_token')
            headers= {'Authorization':"{0} {1}".format('Bearer',access_token)}
            answer = req.post(url='https://kapi.kakao.com/v1/user/logout',data=None,headers=headers)
            answer = json.loads(answer.text)
            print(answer)
            del request.session['code']
            del request.session['doctorid']
            return render(request,'signin.html')

    return render(request, 'signin.html')
def profile(request):
    if 'doctorid' in request.session:
        doctorid = request.session.get('doctorid')
        doctoracc = DoctorAccounts.objects.get(doctorid=doctorid)
        speclist = doctoracc.speclist
        print("#####")
        print(type(speclist))
        speclist = (speclist.replace('\'','').replace('[','').replace(']',''))
        return render(request,'profile.html',context={'doctoracc' : doctoracc,'speclist':speclist})
    return render(request, 'signin.html')
def edit_profile(request):
    if request.method == "POST":
        postdata = request.POST.dict()
        filedata = None
        if 'file' in request.FILES:
            filedata = request.FILES['file']
            filename = filedata.name
        try:
            speclist = []
            speclist = postdata['speclist'].split(',')
            doctorid = request.session.get('doctorid')
            doctoracc = DoctorAccounts.objects.get(doctorid=doctorid)
            doctoracc.doctorname = postdata['doctorname']
            doctoracc.doctorphone = postdata['doctorphone']
            doctoracc.doctoremail = postdata['doctoremail']
            doctoracc.hospitalname = postdata['hospitalname']
            if filedata is not None:
                fp = open(filename,'wb')
                for chunk in filedata.chunks():
                    fp.write(chunk)
                fp.close()
                url = str(uploadIMG(filename)).split('?')[0]
                doctoracc.profileimgurl = url
            doctoracc.speclist =str(speclist)
            doctoracc.save()
            if 'doctorid' in request.session:
                doctorid = request.session.get('doctorid')
                doctoracc = DoctorAccounts.objects.get(doctorid=doctorid)
                speclist = doctoracc.speclist
                speclist = (speclist.replace('\'', '').replace('[', '').replace(']', '').replace(', ',','))
                return render(request, 'profile.html', context={'doctoracc': doctoracc, 'speclist': speclist})
        except Exception as exc:
            return render(request, 'signin.html')

    return render(request, 'signin.html')
def error(request):
    return render(request,'404.html')

def wallet(request):
    return render(request,'wallet.html')
def get_week_content(request):
    if 'week_num' in request.GET.dict():
        print(request.GET.dict())
        week_num = request.GET.dict()['week_num']
        weekurl = Weeks.objects.filter(weekid=week_num)
        arr = []
        for i in weekurl:
            content = i.weekcontents
            url = i.week_url
            # if content.find('[') > -1:
            #     content = ast.literal_eval(content)
            # else:
            #     content = [content]
            # if url != None:
            #     if url.find('[') > -1:
            #         url = ast.literal_eval(url)
            #     else:
            #         url = [url]
            arr.append({
                'topic' : i.week_topic,
                'content' : content,
                'url' : url,
                'key' : i.key

            })
        return HttpResponse(json.dumps({
            'result' : arr
        }))
    return HttpResponse(json.dumps({
        'result' : 'err'
    }))
def hint(request):
    return render(request,'hint.html')



def reply_status(request): # 0 : 아직 의사에게 보내지 않은상태 , 1: 의사에게 보냈지만 의사가 답장하지 않은상태 , 2: 의사가 추가적인 요청을 한 상태, 3: 의사의 답장이 온 상태
    result = -1
    if request.method=="GET":
        getdata = request.GET.dict()
        if 'child_id' in getdata:
            child_id = getdata['child_id']
            week_id = int(UserAccounts.objects.filter(usertoken=child_id)[0].week)
            if week_id == 1:
                week_obj = Week1.objects
            elif week_id == 2:
                week_obj = Week2.objects
            elif week_id == 3:
                week_obj = Week3.objects
            else :
                week_obj = Week4.objects
            if week_obj.filter(childid=child_id,sender=False).count() > 0:
                result = 1
            else:
                result = 0
    return HttpResponse(json.dumps({
        'week_id' : week_id,
        'result' : result
    }))



    #     if 'child_id' in  getdata and 'week_id' in getdata:
    #         child_id = getdata['child_id']
    #         week_id = int(getdata['week_id'])
    #         week_obj = None
    #         if week_id == 1:
    #             week_obj = Week1.objects.filter(childid=child_id)
    #         if week_id == 2:
    #             week_obj = Week2.objects.filter(childid=child_id)
    #         if week_id == 3:
    #             week_obj = Week3.objects.filter(childid=child_id)
    #         if week_id == 4:
    #             week_obj = Week4.objects.filter(childid=child_id)
    #         result = 0
    #         if week_obj.count() > 0:
    #             for i in week_obj:
    #                 if week_obj.filter(sender=True).count() > week_obj.filter(sender=False).count():
    #                     result = 1
    #                 elif week_obj.filter(sender=True).count() < week_obj.filter(sender=False).count():
    #                     result = 2
    #                 elif week_obj.filter(sender=True).count() == week_obj.filter(sender=False).count():
    #                     result = 3
    #         return HttpResponse(json.dumps(
    #             {'result': result}
    #         ))
    # return HttpResponse(json.dumps({
    #     {
    #         'result' : 'err'
    #     }
    # }))

def send_to_child_log(request):
    if request.method == "GET":
        getdata = request.GET.dict()
        if 'child_id' in getdata and 'key' in getdata:
            userid = getdata['child_id']
            key = getdata['key']
            weekobj = Weeks.objects.filter(key=key)
            quest_arr = []
            if weekobj.count() > 0:
                for i in weekobj:
                    quest_arr=i.week_quest.split('\\n')
                    break
                resultobj = quest_arr
                return HttpResponse(json.dumps(
                    {
                        'result' : resultobj
                    }
                ))





            # if Week4.objects.filter(childid=userid,sender=False).count() > 0 :
            #     weekobj = Week4.objects.filter(childid=userid,sender=False)
            # elif Week3.objects.filter(childid=userid,sender=False).count() > 0:
            #     weekobj = Week3.objects.filter(childid=userid,sender=False)
            # elif Week2.objects.filter(childid=userid,sender=False).count() > 0:
            #     weekobj = Week2.objects.filter(childid=userid,sender=False)
            # elif Week1.objects.filter(childid=userid,sender=False).count() > 0:
            #     weekobj = Week1.objects.filter(childid=userid,sender=False)
            # resultobj = []
            # for i in weekobj:
            #     arr = i.content.split('\\n')
            #     resultobj = arr
            #     # resultobj = (ast.literal_eval(i.title))
            # result = json.dumps({
            #     'result' : resultobj
            # })
            # return HttpResponse(result)
    result = json.dumps({
        'result' : 'err'
    })
    return HttpResponse(result)
def send_to_doctor_log(request):
    if request.method == "GET":
        getdata = request.GET.dict()
        if 'child_id' in getdata:
            userid = getdata['child_id']
            weekobj = None
            if Week4.objects.filter(childid=userid,sender=True).count() > 0 :
                weekobj = Week4.objects.filter(childid=userid,sender=True)
            elif Week3.objects.filter(childid=userid,sender=True).count() > 0:
                weekobj = Week3.objects.filter(childid=userid,sender=True)
            elif Week2.objects.filter(childid=userid,sender=True).count() > 0:
                weekobj = Week2.objects.filter(childid=userid,sender=True)
            elif Week1.objects.filter(childid=userid,sender=True).count() > 0:
                weekobj = Week1.objects.filter(childid=userid,sender=True)
            resultobj = []
            for i in weekobj:

                resultobj = ast.literal_eval(i.content)
            result = json.dumps({
                'result' : resultobj
            })
            return HttpResponse(result)
    result = json.dumps({
        'result' : 'err'
    })
    return HttpResponse(result)
def send_to_doctor(request):
    if request.method == "POST":
        postdata = json.loads(request.body.decode('utf-8'))
        print(postdata)
        if 'child_id'in postdata and 'contents' in postdata and 'key' in postdata:
            child_id = postdata['child_id']
            contents = postdata['contents']
            titles = postdata['questions']
            key = postdata['key']
            if key == "tree" or key == "house" or key == "person":
                weekobj = Week1.objects
            elif key == "face_me" or key == "face_friends":
                weekobj = Week2.objects
            elif key == "face_father":
                weekobj = Week3.objects
            else:
                weekobj = Week4.objects
            # if Week1.objects.filter(childid=child_id,sender=True).count() == 0:
            #     weekobj = Week1.objects
            # elif Week2.objects.filter(childid=child_id,sender=True).count() == 0:
            #     weekobj = Week2.objects
            # elif Week3.objects.filter(childid=child_id,sender=True).count() == 0:
            #     weekobj = Week3.objects
            # elif Week4.objects.filter(childid=child_id,sender=True).count() == 0:
            #     weekobj = Week4.objects
            doctor_id = UserAccounts.objects.filter(usertoken=child_id)[0].doctorid
            for i in range(len(contents)):
                weekobj.create(
                doctorid = doctor_id,
                childid = child_id,
                sender = True,
                content = contents[i],
                title = titles[i],
                request_type = False
                ).save()

            return HttpResponse(json.dumps({
                'result' : 'success'
            }))
    return HttpResponse(json.dumps({
        'result' : 'err'
    }))
def doctor_result(request):
    if request.method == "GET":
        getdata = request.GET.dict()
        if 'child_id' in getdata and 'week_id' in getdata:
            child_id = getdata['child_id']
            week_id = int(getdata['week_id'])
            if week_id == 1:
                week_obj = Week1.objects
            elif week_id == 2:
                week_obj = Week2.objects
            elif week_id == 3:
                week_obj = Week3.objects
            else:
                week_obj = Week4.objects
            arr = []
            if week_obj.filter(childid=child_id,sender=False).count() > 0:
                arr.append(week_obj.filter(childid=child_id,sender=False)[0].content)
                return HttpResponse(json.dumps({
                    'result' : arr
                }))
    return HttpResponse(json.dumps({
        'result' : "err"
    }))

# -*-coding:utf-8-*-