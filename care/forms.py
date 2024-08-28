from django import forms
from django.forms import ModelForm,formset_factory,inlineformset_factory
from .models import Supply, Donation, Request, SupplyShipment, SupplyTrans, Notification
from .models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CreateFormUser(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email','password1','password2']


class BenefactorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Benefactor
        fields = ['ben_name', 'ben_phno', 'ben_email', 'ben_pref','org']
        
        
class Benefactor(forms.ModelForm):

        class Meta:
            model = Benefactor
            fields = '__all__'
            exclude = ['user']



class SupplyForm(forms.ModelForm):
    class Meta:
        model = Supply
        exclude = ['user']
        fields = ['supply_type', 'supply_category', 'supply_quantity', 'supply_unit', 'expiration_date', 'supply_descr', 'supply_condition','user']
        widgets = {
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }

# class DonationForm(forms.ModelForm):
#     class Meta:
#         model = Donation
#         fields = ['donor', 'supply', 'quantity_donated', 'donation_date']
#         widgets = {
#             'donation_date': forms.DateInput(attrs={'type': 'date'}),
#         }

class RequestForm(forms.ModelForm):
    supply = forms.ModelChoiceField(queryset=Supply.objects.all(), empty_label="Select Supply", label="Supply Item")

    class Meta:
        model = Request
        fields = ['supply', 'quantity_req', 'req_date', 'priority', 'comments', 'reason', 'dest_loc']
        widgets = {
            'dest_loc': forms.TextInput(attrs={'placeholder': 'Enter location'})
        }

# class SupplyShipmentForm(forms.ModelForm):
#     class Meta:
#         model = SupplyShipment
#         fields = ['request', 'supply', 'quantity_shipped', 'shipment_date', 'expected_delivery', 'actual_delivery', 'delivery_status', 'tracking_no', 'delivery_comments']
#         widgets = {
#             'shipment_date': forms.DateInput(attrs={'type': 'date'}),
#             'expected_delivery': forms.DateInput(attrs={'type': 'date'}),
#             'actual_delivery': forms.DateInput(attrs={'type': 'date'}),
#         }

# class SupplyTransForm(forms.ModelForm):
#     class Meta:
#         model = SupplyTrans
#         fields = ['supply', 'benefactor', 'trans_type', 'trans_quantity', 'trans_date', 'trans_comments']
#         widgets = {
#             'trans_date': forms.DateInput(attrs={'type': 'date'}),
#         }

# class NotificationForm(forms.ModelForm):
#     class Meta:
#         model = Notification
#         fields = ['recipient', 'notif_type', 'message', 'timestamp', 'is_read']
#         widgets = {
#             'timestamp': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#         }



class IDProofForm(forms.ModelForm):
    class Meta:
        model = IDProof
        exclude = ['benefactor']
        fields = [ 'proof_type', 'proof_number', 'issue_date', 'expiry_date', 'proof_document']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'proof_document': forms.FileInput()  # Use FileInput for single file upload
        }