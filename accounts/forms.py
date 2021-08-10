from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Profile


class UserCreateForm(UserCreationForm):
    pass


class UserEditForm(UserChangeForm):
    # 自動で表示されるパスワードフィールドを消す
    password = None

    class Meta:
        model = User
        fields = (
            'username', 'email'
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'nickname', 'bio', 'avatar'
        )
