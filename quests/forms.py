from django import forms
from .models import QuestStepCompletion


class QuestStepCompletionForm(forms.ModelForm):
    class Meta:
        model = QuestStepCompletion
        fields = ['notes', 'evidence']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Add any notes about this step...'}),
            'evidence': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,video/*,application/pdf'}),
        }
