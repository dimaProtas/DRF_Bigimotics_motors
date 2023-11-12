from django.core.exceptions import ValidationError


def get_path_track_list_cover_album(instance, file):
    '''Построение пути к файлу изображение плайлиста'''
    return f'music/playlist/{instance.id}/{file}'


def get_path_upload_track_file(instance, file):
    '''Построение пути к файлу изображение плайлиста'''
    return f'music/track/{instance.id}/{file}'


def validate_size_img(file_obj):
    megabyte_limit = 2
    if file_obj.size > megabyte_limit * 1024 * 1024:
        return ValidationError(f'Максимальный размер файла {megabyte_limit}MB')