import django.forms as forms
from .models import *
from django.contrib.auth.forms import UserChangeForm


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ('students','team_id')
        widgets = {
            "students":forms.SelectMultiple(attrs={"class":"form-control js-states"}),
            "team_id":forms.TextInput(attrs={"class":"form-control"})
        }


class AdminChange(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username','avatar',)
        widgets = {
            "username":forms.TextInput(attrs={"class":"form-control","readonly":"readonly"}),
            # "avatar":forms.FileInput(attrs={"class":"form-control"})
        }

class StudentChange(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username','avatar',)
        widgets = {
            "username":forms.TextInput(attrs={"class":"form-control","readonly":"readonly"}),
            # "avatar":forms.FileInput(attrs={"class":"form-control"})
        }
