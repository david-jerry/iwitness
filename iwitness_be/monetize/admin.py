from django.contrib import admin

from .models import Banks, UserBankAccount, UserEarning

# Register your models here.
admin.site.register(Banks)
admin.site.register(UserBankAccount)
admin.site.register(UserEarning)
