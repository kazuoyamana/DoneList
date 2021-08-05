from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from accounts.views import SignUpView, UserLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('task.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup', SignUpView.as_view(), name="signup"),
    path('accounts/login', UserLoginView.as_view(), name="login"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]