import os
import shutil

from PIL import Image
from django.conf import settings
from django.conf.global_settings import MEDIA_ROOT
from django.core.files.storage import default_storage as storage
from imagekit.utils import get_cache


def img_resize(user, file_name):
    def get_uploaded_file_path(file_name):
        file_path = os.path.join(MEDIA_ROOT, 'user', f'user_{user.id}', file_name)
        uploaded_file_path = storage.open(
            file_path
        )
        return uploaded_file_path

    uploaded_file_path = get_uploaded_file_path(file_name)
    img_origin = Image.open(uploaded_file_path)

    # img1 = img_origin.thumbnail((50, 50))
    img1 = img_origin.resize((100, 100))
    img2 = img_origin.resize((250, 250))
    img3 = img_origin.resize((500, 500))

    directory = os.path.join(settings.MEDIA_ROOT, f'user/user_{user.pk}')
    # 경로가 없으면 만들어줌
    if not os.path.exists(directory):
        os.makedirs(directory)

    # img1
    img1.save(f'../.media/user/user_{user.id}/img_profile_100.png')

    # img2
    filename = f'img_profile_250.png'
    profile_dir = os.path.join(directory, filename)
    img2.save(profile_dir)

    # img3
    profile_dir = os.path.join(directory, 'img_profile_500.png')
    img3.save(profile_dir)


def clear_imagekit_cache():
    cache = get_cache()
    cache.clear()
    # Clear IMAGEKIT_CACHEFILE_DIR
    cache_dir = os.path.join(settings.MEDIA_ROOT, settings.IMAGEKIT_CACHEFILE_DIR)
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)


def clear_imagekit_cache_house_cover(user_pk, house_pk):
    cache = get_cache()
    cache.clear()
    # Clear IMAGEKIT_CACHEFILE_DIR
    cache_dir = os.path.join(settings.MEDIA_ROOT, settings.IMAGEKIT_CACHEFILE_DIR)
    img_profile_dir = os.path.join(cache_dir, f'house/user_{user_pk}/house_{house_pk}')
    if os.path.exists(img_profile_dir):
        shutil.rmtree(img_profile_dir)


def clear_imagekit_cache_img_profile(pk):
    cache = get_cache()
    cache.clear()
    # Clear IMAGEKIT_CACHEFILE_DIR
    cache_dir = os.path.join(settings.MEDIA_ROOT, settings.IMAGEKIT_CACHEFILE_DIR)
    img_profile_dir = os.path.join(cache_dir, f'user/user_{pk}/img_profile')
    if os.path.exists(img_profile_dir):
        shutil.rmtree(img_profile_dir)


def clear_imagekit_test_files():
    clear_imagekit_cache()
    for fname in os.listdir(settings.MEDIA_ROOT):
        if fname != 'reference.png':
            path = os.path.join(settings.MEDIA_ROOT, fname)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
