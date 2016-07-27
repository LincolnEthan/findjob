from django import forms
from pagedown.widgets import PagedownWidget
class SearchForm(forms.Form):
    search=forms.CharField(widget=PagedownWidget())