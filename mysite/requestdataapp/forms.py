from django import forms
from .validators import validate_file_name

class UserBioForm(forms.Form):
    name = forms.CharField(label="Your name", max_length=100)
    age = forms.IntegerField(label="Your age", min_value=1, max_value=99)
    bio = forms.CharField(label="Biography", widget=forms.Textarea)


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField(validators=[validate_file_name])
