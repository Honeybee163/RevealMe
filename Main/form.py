from django import forms
from .models import Message,Riddle

class MessageForm(forms.ModelForm):
    """Form definition for Message."""

    class Meta:
        """Meta definition for Messageform."""

        model = Message
        fields = ['message']
        




class RiddleForm(forms.ModelForm):
    """Form definition for Riddle."""

    class Meta:
        """Meta definition for Riddleform."""

        model = Riddle
        fields = ['riddle','answer','hint']
