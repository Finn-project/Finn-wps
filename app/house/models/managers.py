import datetime

from PIL import Image
from django.db import models
from rest_framework import status

from utils.exception.custom_exception import CustomException


class HouseDisableDayManager(models.Manager):
    def get_or_create(self, date):
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise CustomException(f'올바른 날짜 형식이 아닙니다 ({date})', status_code=status.HTTP_400_BAD_REQUEST)

        return super().get_or_create(date=date)


class HouseImageManager(models.Manager):
    def create_image(self, image):
        try:
            Image.open(image).verify()
        except OSError:
            raise CustomException(f'올바른 이미지 파일 형식이 아닙니다. ({image.name})', status_code=status.HTTP_400_BAD_REQUEST)

        return self.create(image=image)
