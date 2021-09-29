from django import forms
from .models import Posts

class NewPost(forms.ModelForm):

    class Meta:
        model = Posts
        fields = ['content',]
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 1})
        }
        labels = {'content': 'New Post'}
