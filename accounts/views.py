from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from .models import User, Profile
from .forms import ProfileForm, UserCreateForm, UserEditForm


class SignUpView(CreateView):
    form_class = UserCreateForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('task:top')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)

        self.object = user
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return super().form_invalid(form)


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'


@login_required
def profile_view(request):

    return render(request, 'accounts/mypage/index.html', {'user': request.user})


@login_required
def profile_edit_view(request):
    # この get_object_or_404 が無くても request.user から取得できる。
    # 必要な理由は未ログインユーザーに対して404を表示するため
    # しかし @login_required を使うことで解消することが出来る

    # user = get_object_or_404(User, pk=request.user.pk)
    user_form = UserEditForm(request.POST or None, request.FILES or None, instance=request.user)

    # profileが存在しない場合、外部キー user.profile を参照した時点で
    # 「RelatedObjectDoesNotExist」が発生する
    # 上記エラーを補足できた場合は新しいユーザーを作るようにする
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        profile = Profile.objects.create(user=request.user)

    prof_form = ProfileForm(request.POST or None, instance=profile)

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



