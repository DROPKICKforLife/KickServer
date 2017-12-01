from django.contrib import admin
from .models import UploadDatas
from .models import UserAccounts
from .models import DoctorAccounts
from .models import Treatment
from .models import Weeks


admin.site.register(UploadDatas)
admin.site.register(UserAccounts)
admin.site.register(DoctorAccounts)
admin.site.register(Treatment)
admin.site.register(Weeks)