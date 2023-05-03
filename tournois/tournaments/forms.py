from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'rows': 1}), label='')
    class Meta:
        model = Comment
        fields = ['message']
        

class ScoreForm(forms.Form):
    score1 = forms.IntegerField(min_value=0, label='Score 1')
    score2 = forms.IntegerField(min_value=0, label='Score 2')