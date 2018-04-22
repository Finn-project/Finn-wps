from django.core.management import BaseCommand

from utils.crawler.airbnb_json import AirbnbCrawler


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('num_of_obj', type=int)

    def handle(self, *args, **options):
        # crawler
        number_of_obj = options['num_of_obj']
        air = AirbnbCrawler(number_of_obj)
        air.get_bootstrapdata()
