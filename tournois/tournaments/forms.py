from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'rows': 1}), label='')
    class Meta:
        model = Comment
        fields = ['message']