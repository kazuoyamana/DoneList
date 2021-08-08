from django.db import models
from django.conf import settings
from django.utils import timezone


class Task(models.Model):

    title = models.CharField('タスクの名前', max_length=128)
    done_at = models.DateField('タスク完了日', null=True, blank=True)
    created_at = models.DateField('タスク作成日', default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='このタスクを作った人', on_delete=models.CASCADE)

    class Meta:
        db_table = 'task'

    def __str__(self):
        return self.title


class Comment(models.Model):
    body = models.TextField('コメント')
    created_at = models.DateField('コメント作成日', default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'comment'

    def __str__(self):
        return self.body

