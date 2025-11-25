from django.db import models
import uuid
# Create your models here.

class WifiPlan(models.Model):
    """
    - These are the product offering persented to the client e.g
    - 10bob per hour
    """
    name_of_product = models.CharField(max_length=50)
    price = models.IntegerField()
    duration_in_minutes = models.IntegerField()
    data_limit_in_mbz = models.IntegerField(null=True, blank=True) # this will be optional for now

    def __str__(self):
        return f"{self.name_of_product} - {self.price}"

class GuestSession(models.Model):
    """
    - This is a guess session table
    """
    # A unoique ID for this session
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    mac_address = models.CharField(max_length=17)
    
    # the phone number our user entered
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    # A simple flag to track if payment is complete
    is_paid = models.BooleanField(default=False)
    
    # timestamp
    created_at = models.DateTimeField(auto_now_add=True) # This will be set on creation
    paid_at = models.DateTimeField(null=True, blank=True) # This will be set once payment has been made
    plan = models.ForeignKey(WifiPlan, on_delete=models.PROTECT, null=True, blank=True)

    # well  formated tring to display the mac-adress payment status
    def __str_(self):
        return f"{self.mac_address} -{self.plan} - {'Paid' if self.is_paid else 'Pending'}"
