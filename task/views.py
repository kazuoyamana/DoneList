import datetime

from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.views import generic

from . import mixins
from .models import Task, Comment
from .forms import AddTaskForm, AddCommentForm


@csrf_protect
def task_delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'DELETE' and request.user == task.created_by:
        task.delete()
        return redirect('task:top')
    else:
        return HttpResponse("<h1>You can't delete task that belongs to someone else.😅</h1>")


@csrf_protect
def task_done(request, task_id, status):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST' and request.user == task.created_by:
        if status == 'true':
            task.done_at = timezone.now()
        else:
            task.done_at = None
        task.save()
        return redirect('task:top')
    else:
        return HttpResponse('<h1>What are you doing here...😅</h1>')


class TopView(mixins.MonthWithTaskMixin, generic.TemplateView):
    template_name = 'task/top.html'
    model = Task
    date_field = 'created_at'

    def dispatch(self, request, *args, **kwargs):

        today = datetime.date.today()

        # 日付のパラメータが無い時（トップページ）は今日を表示
        if kwargs.get('year') is None:
            kwargs['year'] = today.year
            kwargs['month'] = today.month
            kwargs['day'] = today.day

        the_day = datetime.date(kwargs['year'], kwargs['month'], kwargs['day'])

        # コメントを取得、なければNoneを入れておく
        try:
            comment = Comment.objects.filter(created_by=request.user, created_at=the_day)[0]
        except IndexError:
            comment = None

        if request.user.is_authenticated:
            tasks = Task.objects.filter(created_by=request.user, created_at=the_day)
            form = AddTaskForm(request.POST or None)

            # コメントが存在すれば編集モードに
            if comment:
                comment_form = AddCommentForm(request.POST or None, instance=comment)
            else:
                comment_form = AddCommentForm(request.POST or None)

            if request.method == 'POST':
                # タスクフォーム処理開始
                if form.is_valid():
                    form = form.save(commit=False)
                    form.created_by = request.user

                    # 今日以外では「選択されている日」をタスクの作成日に入れる
                    if today != the_day:
                        form.created_at = the_day

                    form.save()

                # コメントフォーム処理開始
                if comment_form.is_valid():
                    comment_form = comment_form.save(commit=False)
                    comment_form.created_by = request.user

                    # 今日以外では「選択されている日」をタスクの作成日に入れる
                    if today != the_day:
                        comment_form.created_at = the_day

                    comment_form.save()

                return redirect('task:day', kwargs['year'], kwargs['month'], kwargs['day'])

            # 明日と昨日を取得
            yesterday = the_day - datetime.timedelta(days=1)
            tomorrow = the_day + datetime.timedelta(days=1)

            task_context = {
                'tasks_of_the_day': tasks,
                'form': form,
                'today': today,
                'yesterday': yesterday,
                'tomorrow': tomorrow,
                'the_day': the_day,
                'comment_form': comment_form,
                'comment': comment,
            }

            context = super().get_context_data(**kwargs)
            context.update(task_context)
            calendar_context = self.get_month_calendar()
            context.update(calendar_context)

            return self.render_to_response(context)
        else:
            return render(request, 'task/top_guest.html')


@login_required
def delete_comment(request, year, month, day):
    """コメントをGETアクセスから削除します"""

    the_day = datetime.date(year, month, day)
    comment = get_object_or_404(Comment, created_by=request.user, created_at=the_day)

    comment.delete()
    return redirect('task:day', year, month, day)



