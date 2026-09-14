from django import forms


class WalletTopUpForm(forms.Form):
    amount = forms.IntegerField(
        min_value=1_000,
        label="Amount (Toman)",
        widget=forms.NumberInput(attrs={"class": "field-control", "inputmode": "numeric"}),
    )


class WalletAppointmentPaymentForm(forms.Form):
    confirm = forms.BooleanField(required=True, initial=True, widget=forms.HiddenInput())
