from django.contrib import admin
from .models import *


# display database tables on admin page
admin.site.register(Action)
admin.site.register(Category)
admin.site.register(Wallet)
admin.site.register(Currency)
admin.site.register(FamilyAccess)
admin.site.register(Profile)
admin.site.register(Objective)
admin.site.register(LogTable)
admin.site.register(WalletMessage)