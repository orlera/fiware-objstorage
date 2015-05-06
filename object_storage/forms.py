from django import forms

class AttachmentForm(forms.Form):
    name = forms.CharField(label = 'name', max_length = 50)
    attachment = forms.FileField(label = 'attachment')
    uploaded_date = forms.DateTimeField(label = 'uploaded_date')
    container = forms.ChoiceField(label = 'conatiner')