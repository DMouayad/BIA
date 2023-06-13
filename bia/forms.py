from django import forms


class UploadFilesForm(forms.Form):
    tasksFile = forms.FileField(required=True)
    linksFile = forms.FileField(required=True)
