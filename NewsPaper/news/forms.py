from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    heading = forms.CharField(max_length=255)
    class Meta:
        model = Post
        fields = [
            'author',
            'category',
            'heading',
            'content'
        ]
