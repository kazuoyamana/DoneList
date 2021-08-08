from django.urls import path
from .views import task_delete, task_done, TopView, delete_comment

app_name = 'task'

urlpatterns = [
    path('', TopView.as_view(), name='top'),
    path('<int:year>/<int:month>/<int:day>/', TopView.as_view(), name='day'),
    path('delete/<int:task_id>/', task_delete, name='delete'),
    path('done/<int:task_id>/<str:status>/', task_done, name='done'),
    path('delete_co/<int:year>/<int:month>/<int:day>/', delete_comment, name='delete_co'),
]