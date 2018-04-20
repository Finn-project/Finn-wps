from django.contrib import admin

from .models import (
    House,
    HouseImage,
    Amenities,
    Facilities,
    HouseDisableDay,
    HouseReserveDay,
)

admin.site.register(House)
admin.site.register(HouseImage)
admin.site.register(Amenities)
admin.site.register(Facilities)
admin.site.register(HouseDisableDay)
admin.site.register(HouseReserveDay)
