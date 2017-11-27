from ..models import Doctors
import json
from django.http import HttpResponse
class Doctor:
    def __init__(self,therapistName,belongName,count,belongHospitalName,specList,profileImageURL):
        self.therapistName = therapistName
        self.belongName = belongName
        self.count = int(count)
        self.belongHospitalName= belongHospitalName
        self.specList = specList
        self.profileImageURL = profileImageURL
        pass
    def getName(self):
        return self.therapistName,self.belongName,self.count,self.belongHospitalName,self.specList,self.profileImageURL
    def save(self):
        Doctors.objects.create(
            therapistName = self.therapistName,
            belongName = self.belongName,
            count = self.count,
            belongHospitalName = self.belongHospitalName,
            specList = self.specList,
            profileImageURL = self.profileImageURL
        ).save()
        print("SAVE SUCCESSED")
def setDoctor(request):
    if request.method == "POST":
        postdata = request.POST.dict()
        therapistName = postdata['therapistName']
        belongName = postdata['belongName']
        count = postdata['count']
        belongHospitalName = postdata['belongHospitalName']
        specList = postdata['specList']
        profileImageURL = postdata['profileImageURL']
        print(therapistName)
        doc = Doctor(therapistName,belongName,count,belongHospitalName,specList,profileImageURL)
        doc.save()
        result = {
            'result':{
                'message' : "successed"
            }
        }
    else:
        result = {
            'result':{
                'message' : "failed"
            }
        }
    result = json.dumps(result)
    return HttpResponse(result)
def getDoctor(request):
    DoctorsROW = Doctors.objects.all()
    DoctorsArr = []
    doctors = []
    for i in DoctorsROW:
        doc = Doctor(i.therapistName,i.belongName,i.count,i.belongHospitalName,i.specList,i.profileImageURL)
        DoctorsArr.append(doc.getName())
        doctors.append({
                'therapistName': i.therapistName,
                'belongName': i.belongName,
                'count': i.count,
                'belongHospitalName': i.belongHospitalName,
                'specList': i.specList,
                'profileImageURL': i.profileImageURL
        })
        result = {
            'result': doctors
        }
        result = json.dumps(result)
    print(result)

    return HttpResponse(result)



