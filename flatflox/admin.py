from django.contrib import admin
from flatflox.models import User, Location, PGModel, Rating, PGPicture, WorkingCities

# Register your models here.
admin.site.register(User)
admin.site.register(Location)
admin.site.register(PGModel)
admin.site.register(Rating)
admin.site.register(PGPicture)
admin.site.register(WorkingCities)