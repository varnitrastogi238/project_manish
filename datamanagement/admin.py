from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(strategy)

admin.site.register(positions)
admin.site.register(stop_symboll)
