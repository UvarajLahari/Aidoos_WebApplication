from django import forms
from django.template.defaultfilters import mark_safe

class OriginForm(forms.Form):
	city=forms.CharField(label=mark_safe('<strong>City </strong>'),max_length=20)

class DestForm(forms.Form):
	city=forms.CharField(label=mark_safe('<strong>City </strong>'),max_length=20)

class RestForm(forms.Form):
	City=forms.CharField(label=mark_safe('<strong>City </strong>'),max_length=20)
	restaurant=forms.CharField(label=mark_safe('<strong>Restaurant </strong>'),max_length=20)