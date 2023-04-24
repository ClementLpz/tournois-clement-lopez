from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'rows': 1}), label='')
    class Meta:
        model = Comment
        fields = ['message']

class ResearchForm(forms.Form):
    research = forms.CharField(label="", max_length=100)