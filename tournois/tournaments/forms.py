from django import forms

class CommentForm(forms.Form):
    message = forms.CharField(label="message", max_length=600)