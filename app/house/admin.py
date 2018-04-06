from django.contrib import admin

from .models import (
    House,
    HouseLocation,
    HouseImage,
    Amenities,
    Facilities,
    RelationWithHouseAndGuest
)

admin.site.register(House)
admin.site.register(HouseLocation)
admin.site.register(HouseImage)
admin.site.register(Amenities)
admin.site.register(Facilities)
admin.site.register(RelationWithHouseAndGuest)
