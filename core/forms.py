from django import forms


class PatientExampleForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    phone_number = forms.CharField(
        max_length=11,
        help_text="Use the same 09123456789 format as the account model.",
    )
    notes = forms.CharField(required=False, widget=forms.Textarea)
    active = forms.BooleanField(required=False, initial=True)
