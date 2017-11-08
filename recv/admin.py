from django.contrib import admin
from .models import UploadDatas
from .models import UserAccounts
from .models import DoctorAccounts



admin.site.register(UploadDatas)
admin.site.register(UserAccounts)
admin.site.register(DoctorAccounts)