from django import forms
from .models import Customer
import calendar
from django.utils import timezone
from datetime import timedelta

class AddRecordForm(forms.ModelForm):
    customer_name = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"form-control"}), label="Customer Name")
    father_name = forms.CharField(required=False,widget=forms.widgets.TextInput(attrs={"class":"form-control"}), label="Father Name")
    nationality = forms.CharField(required=False,widget=forms.widgets.TextInput(attrs={"class":"form-control"}), label="Nationality")
    cnic = forms.CharField(required=False,widget=forms.widgets.TextInput(attrs={"class":"form-control"}), label="CNIC/Passport Number")
    phone_number = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"form-control"}), label="Phone Number")
    emergency_number = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"form-control"}), label="Emergency Number")
    address = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"form-control"}), label="Address")
    relationship = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"form-control"}), label="Relationship")
    voucher_number = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"form-control"}), label="Voucher Number")
    monthly_fee = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"form-control"}), label="Monthly Fee")
    assigned_trainer = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"form-control"}), label="Assigned Trainer")
    special_training_fee = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"form-control"}), label="Special Training Fee")
    package = forms.CharField(label="Package", widget=forms.Select(choices=Customer.PACKAGE_CHOICES, attrs={"class":"form-control"}))
    remarks = forms.CharField(required=False, widget=forms.widgets.Textarea(attrs={"class":"form-control"}), label="Remarks")

    due_date = forms.DateField(label="Due Date", widget=forms.widgets.DateInput(attrs={'type': 'date', "class":"form-control"}), initial=timezone.now() + timedelta(days=(calendar.monthrange(timezone.now().year, timezone.now().month)[1])))


    class Meta:
        model = Customer
        exclude = ("user",)