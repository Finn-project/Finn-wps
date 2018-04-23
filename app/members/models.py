import os
from django.conf import settings

from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models
from django.db.models import Manager
from django.db.models.signals import post_delete
from django.dispatch import receiver
from imagekit.models import ImageSpecField, ProcessedImageField
from pilkit.processors import ResizeToFill


def dynamic_img_profile_path(instance, file_name):
    return f'user/user_{instance.user.id}/{file_name}'


class UserManager(DjangoUserManager):
    def create_django_user(self, *args, **kwargs):
        user = User.objects.create_user(
            username=kwargs.get('username'),
            email=kwargs.get('username'),
            password=kwargs.get('password'),
            first_name=kwargs.get('first_name', ''),
            last_name=kwargs.get('last_name', ''),
            phone_num=kwargs.get('phone_num', ''),
            is_email_user=True,
        )
        # default profile_image 생성
        # file = open('../.static/img_profile_default.png', 'rb').read()
        # img = UserProfileImages.objects.create(user=user)
        # img.img_profile.save('img_profile.png', ContentFile(file))
        return user

    def create_facebook_user(self, *args, **kwargs):
        pass


class User(AbstractUser):
    file_path = os.path.join(settings.STATIC_DIR, 'img_profile_default.png')

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)

    phone_num = models.CharField(max_length=20, blank=True)
    is_facebook_user = models.BooleanField(default=False)
    is_email_user = models.BooleanField(default=False)

    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)

    is_host = models.BooleanField(default=False)

    objects = UserManager()

    def __str__(self):
        return f'{[self.pk]} {self.username}'


class HostManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_host=True)


class Host(User):
    objects = HostManager()

    class Meta:
        proxy = True

    def __str__(self):
        return f'{self.username} (호스트)'


class GuestManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_host=False)


class Guest(User):
    objects = GuestManager()

    class Meta:
        proxy = True

    def __str__(self):
        return f'{self.username} (게스트)'


class UserProfileImages(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='images'
    )

    img_profile = models.ImageField(upload_to=dynamic_img_profile_path, blank=True, default='')

    # img_profile_28 = ImageSpecField(source='img_profile',
    #                                   processors=[ResizeToFill(28, 28)],
    #                                   format='png',
    #                                   options={'quality': 100})
    #
    # img_profile_225 = ImageSpecField(source='img_profile',
    #                                   processors=[ResizeToFill(225, 225)],
    #                                   format='png',
    #                                   options={'quality': 100})

    # img_profile = ProcessedImageField(blank=True, default='',
    #                                        upload_to=dynamic_img_profile_path,
    #                                        processors=[ResizeToFill(500, 500)],
    #                                        format='png',
    #                                        options={'quality': 100})
    # 원본을 활용할 일이 많기 때문에 ProcessedImageField 대신 원본 이미지 저장
    # * 4/12 Django에서 2MB 이상은 막기때문에 너무 큰 이미지 파일 업로드는 걱정하지 않아도 됨

    img_profile_28 = ProcessedImageField(blank=True, default='',
                                           upload_to=dynamic_img_profile_path,
                                           processors=[ResizeToFill(28, 28)],
                                           format='png',
                                           options={'quality': 100})

    img_profile_225 = ProcessedImageField(blank=True, default='',
                                           upload_to=dynamic_img_profile_path,
                                           processors=[ResizeToFill(225, 225)],
                                           format='png',
                                           options={'quality': 100})

    class Meta:
        verbose_name_plural = '사용자 프로필이미지'

    def __str__(self):
        return f'{self.user}의 프로필사진 | {self.img_profile.name}'


@receiver(post_delete, sender=UserProfileImages)
def remove_file_from_storage(sender, instance, using, **kwargs):
    # if os.path.isfile(instance.img_profile.path):
    #     print(instance.img_profile.path)
    #     img_url = instance.img_profile.url
    #     print(img_url)
    # -> 4/12 S3에 deploy한 환경에서 os.path(?) 또는
    # instance.img_profile.path(?)를 쓰면
    # 주소를 읽지못해 에러 발생
    # clear_imagekit_cache_img_profile(instance.pk)
    if instance.img_profile:
        instance.img_profile.delete(save=False)
        instance.img_profile_28.delete(save=False)
        instance.img_profile_225.delete(save=False)


# @receiver(post_save, sender=UserProfileImages)
# def remove_file_from_storage(sender, instance, using, **kwargs):
#     # if os.path.isfile(instance.img_profile.path):
#     #     print(instance.img_profile.path)
#     #     img_url = instance.img_profile.url
#     #     print(img_url)
#     # -> 4/12 S3에 deploy한 환경에서 os.path(?) 또는
#     # instance.img_profile.path(?)를 쓰면
#     # 주소를 읽지못해 에러 발생
#
#     if instance.img_profile:
#         instance.img_profile.delete(save=False)
