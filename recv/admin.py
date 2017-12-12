from django.contrib import admin
from .models import UploadDatas
from .models import UserAccounts
from .models import DoctorAccounts
from .models import Weeks
from .models import Week1


admin.site.register(UploadDatas)
admin.site.register(UserAccounts)
admin.site.register(DoctorAccounts)
admin.site.register(Weeks)
admin.site.register(Week1)