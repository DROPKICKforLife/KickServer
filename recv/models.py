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
    createdate = models.DateTimeField('createdate',auto_now=True)
    week = models.IntegerField('week',default=1)
    doctorid = models.IntegerField('doctorid',null=True)
    # userID = models.TextField('USERID',max_length=20)
    # userPW = models.TextField('USERPW',max_length=20)
    # phone = models.TextField('PHONE',max_length=11)
    # sex = models.CharField('SEX',max_length=1)
    pass

class UploadDatas(models.Model):
    userid = models.IntegerField('userid',null=False)
    dataurl = models.TextField('dataurl',max_length=200)
    uploadtime = models.DateTimeField('uploadtime',auto_now=True)
    content = models.TextField('content',max_length=1000, null=True) # 분석내용

    pass
class DoctorAccounts(models.Model):
    # doctortoken = models.BigIntegerField('doctortoken',null=True)
    doctorid = models.IntegerField('doctorid')
    doctorkakaoid = models.TextField('doctorkakaoid',max_length=100)
    doctorcount = models.IntegerField('doctorcount',default=0)
    doctorphone = models.TextField('doctorphone',max_length=20,null=True)
    doctorname = models.TextField('doctorname',max_length=50, null=True)
    doctoremail = models.TextField('doctoremail',max_length=50,null=True)
    hospitalname = models.TextField('hospitalname',max_length=50, null=True)
    profileimgurl = models.TextField('profileimgurl',max_length=200, null=True)
    speclist = models.TextField('speclist',max_length=500 , null=True)
    schoolname = models.TextField('schoolname',max_length=50, null=True)
    registerdate = models.DateTimeField('registerdate',auto_now=True)
    confirm = models.BooleanField('confirm',default=False)
    pass
class Weeks(models.Model):
    id = models.AutoField('id',primary_key=True)
    weekid = models.IntegerField('weekid',null=True)
    weekcontents = models.TextField('weekcontents',max_length=500) #???????
    week_url = models.TextField('week_url',max_length=500) # week content's url
    week_topic = models.TextField('week_topic',max_length=500,null=True)
    key = models.TextField('key',max_length=100,null=True)
    week_quest = models.TextField('week_quest',max_length=500,null=True)
class Week1(models.Model):
    id = models.AutoField('id',primary_key=True)
    doctorid = models.IntegerField('doctorid')
    childid = models.IntegerField('childid')
    sender = models.BooleanField('sender',default=False) # 0 : 의사->아이 1 : 아이->의사
    content = models.TextField('content',max_length=500,null=True)
    title = models.TextField('title',max_length=500,null=True)
    date = models.DateTimeField('date',auto_now=True, null=True)
    request_type = models.BooleanField('request_type', null=False)
class Week2(models.Model):
    id = models.AutoField('id',primary_key=True)
    doctorid = models.IntegerField('doctorid')
    childid = models.IntegerField('childid')
    sender = models.BooleanField('sender',default=False) # 0 : 의사->아이 1 : 아이->의사
    content = models.TextField('content',max_length=500,null=True)
    title = models.TextField('title',max_length=500,null=True)
    date = models.DateTimeField('date',auto_now=True, null=True)
    request_type = models.BooleanField('request_type', null=False)

class Week3(models.Model):
    id = models.AutoField('id',primary_key=True)
    doctorid = models.IntegerField('doctorid')
    childid = models.IntegerField('childid')
    sender = models.BooleanField('sender',default=False) # 0 : 의사->아이 1 : 아이->의사
    content = models.TextField('content',max_length=500,null=True)
    title = models.TextField('title',max_length=500,null=True)
    date = models.DateTimeField('date',auto_now=True, null=True)
    request_type = models.BooleanField('request_type', null=False)

class Week4(models.Model):
    id = models.AutoField('id',primary_key=True)
    doctorid = models.IntegerField('doctorid')
    childid = models.IntegerField('childid')
    sender = models.BooleanField('sender',default=False) # 0 : 의사->아이 1 : 아이->의사
    content = models.TextField('content',max_length=500,null=True)
    title = models.TextField('title',max_length=500,null=True)
    date = models.DateTimeField('date',auto_now=True, null=True)
    request_type = models.BooleanField('request_type', null=False)



