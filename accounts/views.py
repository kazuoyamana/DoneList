from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User

from .models import Profile
from .forms import ProfileForm, UserCreateForm, UserEditForm


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('task:top')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.add_message(self.request, messages.SUCCESS, '会員登録に成功しました。')

        self.object = user
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, '会員登録に失敗しました。')
        return super().form_invalid(form)


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'


def profile_view(request):
    user = get_object_or_404(User, id=request.user.pk)

    return render(request, 'accounts/mypage/index.html', {'user': user})


def profile_edit_view(request):
    user_form = UserEditForm(request.POST or None, instance=request.user)
    prof_form = ProfileForm(request.POST or None, files=request.FILES or None, instance=request.user.profile)
    if request.method == 'POST' and user_form.is_valid() and prof_form.is_valid():

        user_form.save()
        prof_form.save()
        messages.add_message(request, messages.SUCCESS, 'ユーザー情報を更新しました。')
        return redirect('account:profile')

    context = {
        'user_form': user_form,
        'prof_form': prof_form,
    }

    return render(request, 'accounts/mypage/edit.html', context)



