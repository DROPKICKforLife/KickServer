from django.db import models




class UploadDatas(models.Model):
    userID = models.TextField('USERID',max_length=20)
    treeURL = models.TextField('TREEURL',max_length=20)
    houseURL = models.TextField('HOUSEURL',max_length=100)
    lastEdit = models.DateTimeField('LASTEDIT',auto_now=True)
    def getID(self):
        return self.userID
    def gettree(self):
        return self.treeURL
    def gethouse(self):
        return self.houseURL
    def getlast(self):
        return self.lastEdit

    pass
class UserAccounts(models.Model):
    userID = models.TextField('USERID',max_length=20)
    userPW = models.TextField('USERPW',max_length=20)
    phone = models.TextField('PHONE',max_length=11)
    sex = models.CharField('SEX',max_length=1)

    pass

class DoctorAccounts(models.Model):
    doctorID = models.TextField('DOCTORID',max_length=20)
    doctorPW = models.TextField('DOCTORPW',max_length=20)
    phone = models.TextField('PHONE',max_length=11)
    sex = models.CharField('SEX',max_length=1)

    pass