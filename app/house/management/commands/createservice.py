from django.core.management import BaseCommand

from ...models import Amenities, Facilities


class Command(BaseCommand):
    def handle(self, *args, **options):
        amenities_list = ['TV', '에어컨', '전자렌지', '커피포트', '컴퓨터', '공기청정기']
        facilities_list = ['수영장', '엘리베이터', '세탁소', '노래방', '오락실', '온천']

        [Amenities.objects.create(name=name) for name in amenities_list]
        [Facilities.objects.create(name=name) for name in facilities_list]
