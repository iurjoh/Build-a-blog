from .models import Comment, Post, Contact
from django import forms


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "featured_image", "excerpt", "content", "status",)


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('email', 'subject', 'message',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get the 'user' argument if provided
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        contact = super().save(commit=False)

        # Set the user if available
        if self.user:
            contact.user = self.user

        if commit:
            contact.save()

        return contact
