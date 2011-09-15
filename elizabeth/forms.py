from django import forms

class UploadFileForm(forms.Form):
    #filename = forms.CharField(max_length=100)
    file = forms.FileField()
    