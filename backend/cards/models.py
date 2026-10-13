from django.db import models
from django.contrib.auth.models import User

class Card(models.Model):
    CARD_TYPES = [
        ('CREDIT', 'CREDIT'),
        ('DEBIT', 'DEBIT'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    cardholder_name = models.CharField(max_length=150)
    card_type = models.CharField(max_length=10, choices=CARD_TYPES, default='CREDIT')
    masked_card_number = models.CharField(max_length=30)
    last_four_digits = models.CharField(max_length=4)
    expiry_month = models.IntegerField()
    expiry_year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'card_management_card'

    def __str__(self):
        return f"{self.card_type} ending in {self.last_four_digits}"