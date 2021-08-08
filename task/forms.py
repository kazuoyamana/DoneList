from django import forms
from .models import Task, Comment


class AddTaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ('title',)


class AddCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('body',)