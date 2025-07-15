from django import forms

class MyVerificationForm(forms.Form):
    verification_code = forms.CharField(max_length=6)

class PasswordChangeForm(forms.Form):
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput)