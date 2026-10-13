from django.db import models
from django.contrib.auth.models import User
from cards.models import Card

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    description = models.CharField(max_length=255, default='Testing')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions_transaction'

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"