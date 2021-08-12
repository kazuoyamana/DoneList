from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Profile, User


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')


class UserEditForm(forms.ModelForm):
    # 自動で表示されるパスワードフィールドを消す
    # password = None

    class Meta:
        model = User
        fields = (
            'username', 'email', 'avatar', 'week_status'
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'website', 'bio',
        )
