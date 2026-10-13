from rest_framework import serializers
from .models import Card

class CardSerializer(serializers.ModelSerializer):
    card_number = serializers.CharField(write_only=True, min_length=16, max_length=19)
    cvv = serializers.CharField(write_only=True, min_length=3, max_length=4, required=False)

    class Meta:
        model = Card
        fields = [
            'id',
            'cardholder_name',
            'card_type',
            'card_number',
            'cvv',
            'last_four_digits',
            'expiry_month',
            'expiry_year',
            'created_at'
        ]
        read_only_fields = ['id', 'last_four_digits', 'created_at']

    def create(self, validated_data):
        raw_number = validated_data.pop('card_number')
        validated_data.pop('cvv', None)  # Never store CVV

        clean_number = raw_number.replace(' ', '').replace('-', '')
        last_4 = clean_number[-4:]
        masked = f"****-****-****-{last_4}"

        card = Card.objects.create(
            user=self.context['request'].user,
            masked_card_number=masked,
            last_four_digits=last_4,
            **validated_data
        )
        return card