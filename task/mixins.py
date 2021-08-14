import calendar
import datetime
import itertools
from collections import deque

from .models import Task, Comment


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
        # カレンダー上に表示するだけなので、その日のタスク・コメントの有無、完了確認だけ取得できれば良い
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

    def get_consecutive_days(self):
        """連続したタスク完了日を返す

        作成日と完了日からタスクが連続して完了している日を算出する。

        Returns:
            list[dict]
        """

        # 完了したタスクのある日だけ取得（Values_list(flat=True）で取得したリストをset化）
        done_dates = set(
            Task.objects.filter(done_at__isnull=False, created_by=self.request.user)
                .values_list('created_at', flat=True)
        )
        # 未完了タスクのある日だけ取得
        not_done_dates = set(
            Task.objects.filter(done_at__isnull=True, created_by=self.request.user)
                .values_list('created_at', flat=True)
        )

        # ２つのセットの差集合からすべて終わっている日付setを作る
        all_done_dates = done_dates - not_done_dates
        # list化してsort
        sorted_dates = sorted(list(all_done_dates))

        result = []
        cur_dic = None
        for i, cur_date in enumerate(sorted_dates):
            if i == 0:
                cur_dic = dict(
                    start_date=cur_date,
                    end_date=cur_date,
                    continuous_days=1
                )
                continue
            if cur_date - datetime.timedelta(days=1) == sorted_dates[i - 1]:
                # 連続
                cur_dic['end_date'] = cur_date
                cur_dic['continuous_days'] += 1
            else:
                # 途切れた
                result.append(cur_dic)
                cur_dic = dict(
                    start_date=cur_date,
                    end_date=cur_date,
                    continuous_days=1
                )
        # 最後のcur_dicを追加
        result.append(cur_dic)

        return result

    def get_best_consecutive(self):
        """get_consecutive_days()から取得したデータをもとに、
        最高継続記録と現在継続中の記録を返す

        Returns:
            dict
        """

        today = datetime.date.today()

        consecutive_days = self.get_consecutive_days()
        # print(consecutive_days)

        # タスクがない場合は処理から抜ける
        if consecutive_days == [None]:
            return

        # 最新の連続記録最終日を取得
        cur_con_last = consecutive_days[-1]['end_date']

        # current_consecutive_day = None

        # 最新の連続記録が、昨日・今日まで続いてたら現在継続中にする
        if cur_con_last == today - datetime.timedelta(days=1) or cur_con_last == today:
            current_consecutive_day = consecutive_days[-1]['continuous_days']
        else:
            current_consecutive_day = 0

        most_consecutive_days = []
        for day in consecutive_days:
            most_consecutive_days.append(day['continuous_days'])

        return {
            'current_consecutive_day': current_consecutive_day,
            'most_consecutive_days': max(most_consecutive_days)
        }

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

