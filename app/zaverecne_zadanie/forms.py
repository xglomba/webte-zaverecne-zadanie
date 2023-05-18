from django import forms


class EquationForm(forms.Form):
    equation = forms.CharField(widget=forms.Textarea)