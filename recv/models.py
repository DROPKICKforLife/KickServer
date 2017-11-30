from django.db import models


class UserAccounts(models.Model):
    userid = models.AutoField('userid',primary_key=True)
    usertoken = models.BigIntegerField('usertoken',null=False)
    childname = models.TextField('childname',max_length=50)
    childsex = models.SmallIntegerField('childsex')
    childbirth = models.DateTimeField('childbirth')
    childability = models.SmallIntegerField('childability')
    prevcontent = models.TextField('prevcontent',max_length=200,null=True)
    hopecontent = models.TextField('hopecontent',max_length=200,null=True)
    # userID = models.TextField('USERID',max_length=20)
    # userPW = models.TextField('USERPW',max_length=20)
    # phone = models.TextField('PHONE',max_length=11)
    # sex = models.CharField('SEX',max_length=1)
    pass

class UploadDatas(models.Model):
    userid = UserAccounts.userid
    dataurl = models.TextField('dataurl',max_length=200)
    uploadtime = models.DateTimeField('uploadtime',auto_now=True)
    # treeURL = models.TextField('TREEURL',max_length=100)
    # houseURL = models.TextField('HOUSEURL',max_length=100)
    # personURL = models.TextField('PERSONURL',max_length=100,null=True)

    pass
class DoctorAccounts(models.Model):
    doctorid = models.AutoField('doctorid',primary_key=True)
    doctorcount = models.IntegerField('doctorcount')
    doctorname = models.TextField('doctorname',max_length=50)
    hospitalname = models.TextField('hospitalname',max_length=50)
    profileimgurl = models.TextField('profileimgurl',max_length=200)
    speclist = models.TextField('speclist',max_length=500)
    schoolname = models.TextField('schoolname',max_length=50)
    pass
class Treatment(models.Model): #진단내역
    treatid = models.AutoField('treatid',primary_key=True)
    userid = UserAccounts.userid
    week = models.IntegerField('week') # week 번호
    state = models.SmallIntegerField('state') # 0 : 답변대기 1 : 답변완료

    reqdate = models.DateTimeField('reqdate') # 요청시간
    reqcontent = models.TextField('reqcontent',max_length=500,null=True) # 요청 내용

    recvdate = models.DateTimeField('recvdate',null=True) #답변시간
    recvcontent = models.TextField('recvcontent',max_length=500,null=True) # 답변 내용
    pass
class Weeks(models.Model):
    weekid = models.AutoField('weekid',primary_key=True)
    weekcontents = models.TextField('weekcontents',max_length=500) #???????
