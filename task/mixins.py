import calendar
import datetime
import itertools
from collections import deque

from .models import Comment


class BaseCalendarMixin:
    """カレンダー関連Mixinの、基底クラス"""
    first_weekday = 0  # 0は月曜から、1は火曜から。6なら日曜日からになります。お望みなら、継承したビューで指定してください。
    week_names = ['月', '火', '水', '木', '金', '土', '日']  # これは、月曜日から書くことを想定します。['Mon', 'Tue'...

    def setup_calendar(self):
        """内部カレンダーの設定処理

        calendar.Calendarクラスの機能を利用するため、インスタンス化します。
        Calendarクラスのmonthdatescalendarメソッドを利用していますが、デフォルトが月曜日からで、
        火曜日から表示したい(first_weekday=1)、といったケースに対応するためのセットアップ処理です。

        """
        self._calendar = calendar.Calendar(self.first_weekday)

    def get_week_names(self):
        """first_weekday(最初に表示される曜日)にあわせて、week_namesをシフトする"""
        week_names = deque(self.week_names)
        week_names.rotate(-self.first_weekday) # リスト内の要素を右に1つずつ移動
        return week_names


class MonthCalendarMixin(BaseCalendarMixin):
    """月間カレンダーの機能を提供するMixin"""

    def get_previous_month(self, date):
        """前月を返す"""
        if date.month == 1:
            return date.replace(year=date.year-1, month=12, day=1)
        else:
            return date.replace(month=date.month-1, day=1)

    def get_next_month(self, date):
        """次月を返す"""
        if date.month == 12:
            return date.replace(year=date.year+1, month=1, day=1)
        else:
            return date.replace(month=date.month+1, day=1)

    def get_month_days(self, date):
        """その月の全ての日を返す"""
        return self._calendar.monthdatescalendar(date.year, date.month)

    def get_current_month(self):
        """現在の月を返す"""
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        if month and year:
            month = datetime.date(year=int(year), month=int(month), day=1)
        else:
            month = datetime.date.today().replace(day=1)
        return month

    def get_month_calendar(self):
        """月間カレンダー情報の入った辞書を返す"""
        self.setup_calendar()
        current_month = self.get_current_month()
        calendar_data = {
            'now': datetime.date.today(),
            'month_days': self.get_month_days(current_month),
            'month_current': current_month,
            'month_previous': self.get_previous_month(current_month),
            'month_next': self.get_next_month(current_month),
            'week_names': self.get_week_names(),
        }
        return calendar_data


class MonthWithTaskMixin(MonthCalendarMixin):
    """タスク付きの、月間カレンダーを提供するMixin"""

    def get_month_tasks(self, start, end, days):
        """それぞれの日とタスクを返す"""

        lookup = {
            # '例えば、done_at__range: (1日, 31日)'を動的に作る
            f'{self.date_field}__range': (start, end),
            'created_by': self.request.user,
        }
        # 例えば、Task.objects.filter(created_at__range=(1日, 31日), created_by=request.user) になる
        queryset = self.model.objects.filter(**lookup)
        comment_qs = Comment.objects.filter(**lookup)

        # {1日のdatetime: ['Done', 'Yet', 'Yet', 'Comment'], 2日のdatetime: ['Done', 'Comment']...}のような辞書を作る
        # 'Done', 'Yet' は各タスクが完了したかどうかを表す。 'Comment' はコメントの有無を表す
        # あくまでカレンダー上に表示するだけなので、その日のタスク・コメントの有無、完了確認だけ取得できれば良い
        day_tasks = {day: [] for week in days for day in week}

        for task in queryset:
            task_date = getattr(task, self.date_field)

            if task.done_at:
                task_status = 'Done'
            else:
                task_status = 'Yet'

            day_tasks[task_date].append(task_status)

        for comment in comment_qs:
            day_tasks[comment.created_at].append('Comment')

        # day_tasks辞書を、週毎に分割する。[{1日: ['Done', 'Yet', 'Comment']}... {8日: ['Done', 'Comment']...}, ...]
        # 7個ずつ取り出して分割しています。
        size = len(day_tasks)
        return [{key: day_tasks[key] for key in itertools.islice(day_tasks, i, i + 7)} for i in range(0, size, 7)]

    def get_month_calendar(self):
        calendar_context = super().get_month_calendar()
        month_days = calendar_context['month_days']
        month_first = month_days[0][0]
        month_last = month_days[-1][-1]
        calendar_context['month_day_tasks'] = self.get_month_tasks(
            month_first,
            month_last,
            month_days
        )
        return calendar_context

