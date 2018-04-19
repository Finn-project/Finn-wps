__all__ = (
    'dynamic_img_house_path',
    'dynamic_img_cover_path',
)


def dynamic_img_house_path(instance, file_name):
    return f'house/user_{instance.house.host.id}/house_{instance.house.pk}/images/{file_name}'


def dynamic_img_cover_path(instance, file_name):
    return f'house/user_{instance.host.id}/house_{instance.pk}/{file_name}'
