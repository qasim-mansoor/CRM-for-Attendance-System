from django import forms
from .models import Customer

class AddRecordForm(forms.ModelForm):
    customer_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Customer Name", "class":"form-control"}), label="")
    father_name = forms.CharField(required=False,widget=forms.widgets.TextInput(attrs={"placeholder":"Father Name", "class":"form-control"}), label="")
    phone_number = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Phone Number", "class":"form-control"}), label="")
    emergency_number = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Emergency Number", "class":"form-control"}), label="")
    address = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Address", "class":"form-control"}), label="")
    package = forms.CharField(label="", widget=forms.Select(choices=Customer.PACKAGE_CHOICES, attrs={"class":"form-control"}))
    remarks = forms.CharField(required=False, widget=forms.widgets.Textarea(attrs={"placeholder":"Remarks", "class":"form-control"}), label="")

    class Meta:
        model = Customer
        exclude = ("user", )