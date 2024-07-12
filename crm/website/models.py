from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
import calendar

# def days_in_month():

#     return calendar.monthrange(dt.year, dt.month)[1]

# Create your models here.
class Customer(models.Model):
    # created_at = models.DateTimeField(auto_now_add=True)
    admission_date = models.DateTimeField(auto_now_add=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    father_name = models.CharField(max_length=255, blank=True, null=True)
    nationality = models.CharField(max_length=255, blank=True, null=True)
    cnic = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    emergency_number = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    relationship = models.CharField(max_length=255, blank=True, null=True)
    voucher_number = models.CharField(max_length=255, blank=True, null=True)
    monthly_fee = models.CharField(max_length=255, blank=True, null=True)
    assigned_trainer = models.CharField(max_length=255, blank=True, null=True)
    special_training_fee = models.CharField(max_length=255, blank=True, null=True)
    last_paid = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)

    PACKAGE_CHOICES = [
        ("Staff Member", "Staff Member"),
        ("Deans Employee", "Deans Employee"),
        ("Resident", "Resident"),
        ("General", "General"),
        ("Student", "Student"),
        ("Other", "Other"),
    ]
    package = models.CharField(max_length=30, blank=True, null=True)

    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return(f"{self.customer_name}")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_last_paid = getattr(self, 'last_paid', None)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._original_last_paid = instance.last_paid
        return instance
    
    def save(self, extend=0, *args, **kwargs):
        extend = int(extend)
        if self._original_last_paid != self.last_paid or self.due_date == None:
            self.due_date = timezone.now() + timedelta(days=(calendar.monthrange(timezone.now().year, timezone.now().month)[1])+extend)
            self._original_last_paid = self.last_paid

        if extend > 0:
            self.due_date = self.due_date + timedelta(days=extend)
        
        # # Calculate due date based on last_paid
        # self.due_date = timezone.now() + timedelta(days=(31+extend))  # Add 31 days for next month
        # # Adjust for edge cases where the next month has less than 31 days
        # if self.due_date.month == timezone.now().month:
        #     # If calculated date falls in the same month, add another month
        super().save(*args, **kwargs)



