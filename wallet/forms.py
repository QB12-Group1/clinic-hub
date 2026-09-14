from django import forms


class WalletTopUpForm(forms.Form):
    amount = forms.IntegerField(
        min_value=1_000,
        label="Amount (Toman)",
        widget=forms.NumberInput(attrs={"class": "field-control", "inputmode": "numeric"}),
    )
