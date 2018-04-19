from django.core.management import BaseCommand

from utils.crawler.airbnb import AirbnbCrawler


class Command(BaseCommand):
    def handle(self, *args, **options):

        # crawler
        air = AirbnbCrawler()
        air.get_bootstrapdata()
