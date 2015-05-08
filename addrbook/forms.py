from django import forms

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from models import *

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=20, label=_('First Name'))
    last_name  = forms.CharField(max_length=20, label=_('Last Name'))
    username   = forms.CharField(max_length=20, label=_('User Name'))
    password1  = forms.CharField(max_length=99, label=_('Password'), 
                                 widget = forms.PasswordInput())
    password2  = forms.CharField(max_length=99, label=_('Confirm Password'),  
                                 widget = forms.PasswordInput())


    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username


class CreateForm(forms.ModelForm):
    class Meta:
        model = Entry
        exclude = (
            'created_by',
            'creation_time',
            'updated_by',
            'update_time',
        )
        labels = {
            "last_name":    _("Last Name"),
            "first_name":   _("First Name"),
            "birthday":     _("Birthday"),
            "address":      _("Address"),
            "city":         _("City"),
            "state":        _("State"),
            "zip_code":     _("Zip Code"),
            "country":      _("Country"),
            "email":        _("Email Address"),
            "home_phone":   _("Home Phone"),
            "cell_phone":   _("Cell Phone"),
            "fax":          _("Fax Number"),
            "spouse_last":  _("Spouse Last"),
            "spouse_first": _("Spouse First"),
            "spouse_birth": _("Spouse Birthday"),
            "spouse_cell":  _("Spouse Cell"),
            "spouse_email": _("Spouse Email"),
        }


class EditForm(forms.ModelForm):
    class Meta:
        model = Entry
        exclude = (
            'created_by',
            'creation_time',
            'updated_by',
        )
        widgets = {
            'update_time': forms.HiddenInput,
        }
        labels = {
            "last_name":    _("Last Name"),
            "first_name":   _("First Name"),
            "birthday":     _("Birthday"),
            "address":      _("Address"),
            "city":         _("City"),
            "state":        _("State"),
            "zip_code":     _("Zip Code"),
            "country":      _("Country"),
            "email":        _("Email Address"),
            "home_phone":   _("Home Phone"),
            "cell_phone":   _("Cell Phone"),
            "fax":          _("Fax Number"),
            "spouse_last":  _("Spouse Last"),
            "spouse_first": _("Spouse First"),
            "spouse_birth": _("Spouse Birthday"),
            "spouse_cell":  _("Spouse Cell"),
            "spouse_email": _("Spouse Email"),
        }

