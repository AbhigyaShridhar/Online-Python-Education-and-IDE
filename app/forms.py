from django import forms
from .models import Lesson
from django_summernote.widgets import SummernoteWidget

class CreateForm(forms.ModelForm):

  class Meta:
    model = Lesson
    fields = ['language', 'title', 'content']
    widgets = {
            'content': SummernoteWidget(),
        }
