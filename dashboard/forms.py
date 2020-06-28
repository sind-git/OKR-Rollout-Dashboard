from django import forms
from .models import Functions

class FunctionsForm(forms.ModelForm):
    class Meta:
        model = Functions
        fields = ('name')
