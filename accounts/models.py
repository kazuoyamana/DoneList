from django.db import models
from django.conf import settings


class Profile(models.Model):
    nickname = models.CharField('ニックネーム', max_length=24)
    bio = models.TextField('自己紹介', max_length=1000, blank=True)
    avatar = models.FileField(upload_to='uploads/', blank=True, default='')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.nickname


