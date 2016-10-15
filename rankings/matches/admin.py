from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Player)
admin.site.register(Activity)
admin.site.register(Result)

admin.site.register(SkillType)
admin.site.register(ResultSet)
admin.site.register(ResultSetMember)
