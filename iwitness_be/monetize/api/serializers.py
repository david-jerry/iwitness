from __future__ import annotations

import requests
from django.conf import settings
from rest_framework import serializers
from thefuzz import fuzz

from ..models import Banks, UserBankAccount, UserEarning


class BanksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banks
        fields = [
            "name",
            "lcode",
            "code",
            "country_iso",
        ]


class UserBankAccountSerializer(serializers.ModelSerializer):
    # Include the BankSerializer for nested representation of 'bank' field
    bank = BanksSerializer(many=False, read_only=True)

    class Meta:
        model = UserBankAccount
        fields = ["id", "verified", "bank", "account_name", "account_number"]

    def validate_account_number(self, value):
        """
        Validate the account number using the Paystack API.

        Args:
        - value: The account number to be validated.

        Returns:
        - str: The validated account number if successful.

        Raises:
        - serializers.ValidationError: If validation fails.
        """
        # Replace 'your_paystack_secret_key' with your actual Paystack secret key
        paystack_api_url = (
            f"https://api.paystack.co/bank/resolve?account_number={value}&bank_code={self.initial_data['bank_code']}"
        )

        # Make a GET request to Paystack API
        response = requests.get(paystack_api_url, headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"})

        # Check if the response is successful
        if response.status_code == 200:
            response_data = response.json()

            # Check if the account number is resolved
            if response_data.get("status") and response_data.get("message") == "Account number resolved":
                # Compare the names for similarity (use your similarity function)
                similarity_score = fuzz.token_sort_ratio(
                    response_data["data"]["account_name"], self.initial_data["account_name"]
                )

                # Define a threshold for similarity (e.g., 70%)
                similarity_threshold = 80

                if similarity_score >= similarity_threshold:
                    # If similar, update the account name with the resolved name
                    self.initial_data["account_name"] = response_data["data"]["account_name"]
                    return value
                else:
                    raise serializers.ValidationError("Account name does not match with Paystack verification.")
            else:
                raise serializers.ValidationError("Paystack account verification failed.")
        else:
            raise serializers.ValidationError("Error connecting to Paystack API.")

    def update(self, instance, validated_data):
        """
        Update the user bank account while ensuring the 'user' field cannot be modified.

        Args:
        - instance: The existing UserBankAccount instance.
        - validated_data: The validated data to update.

        Returns:
        - UserBankAccount: The updated UserBankAccount instance.
        """
        # Ensure the user cannot update the `user`
        validated_data.pop("user", None)
        return super().update(instance, **validated_data)

    def to_representation(self, instance):
        """
        Custom method to include the 'user' field in the serialized representation.

        Args:
        - instance: The UserBankAccount instance being serialized.

        Returns:
        - dict: The serialized representation of the UserBankAccount instance.
        """
        ret = super().to_representation(instance)
        ret["user"] = instance.user.username
        return ret


class UserEarningSerializer(serializers.ModelSerializer):
    class Meta:
        # Define the model and fields to include in the serializer
        model = UserEarning
        fields = ["id", "balance"]

    def to_representation(self, instance):
        """
        Custom method to include the 'user' field in the serialized representation.

        Args:
        - instance: The UserEarning instance being serialized.

        Returns:
        - dict: The serialized representation of the UserEarning instance.
        """
        # Use the default representation and add the 'user' field
        ret = super().to_representation(instance)

        # Add the 'user' field, representing the username of the user associated with the UserEarning
        ret["user"] = instance.user.username

        return ret
