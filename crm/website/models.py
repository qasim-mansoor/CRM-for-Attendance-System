from django.db import models
from django.utils import timezone

# Create your models here.
class Customer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15)
    emergency_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    last_paid = models.DateTimeField(auto_now_add=True)

    PACKAGE_CHOICES = [
        ("Student", "Student"),
        ("General", "General"),
        ("Resident", "Resident"),
    ]
    package = models.CharField(max_length=30, choices=PACKAGE_CHOICES)

    remarks = models.TextField(blank=True)

    def __str__(self):
        return(f"{self.customer_name}")



