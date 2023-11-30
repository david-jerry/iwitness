from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from config.pagination import CustomPagination
from iwitness_be.monetize.models import Banks, UserBankAccount, UserEarning
from iwitness_be.utils.permissions import IsOwnerOrStaff

from .serializers import BanksSerializer, UserBankAccountSerializer, UserEarningSerializer

User = get_user_model()


class BankViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = Banks.objects.all()
    serializer_class = BanksSerializer
    lookup_field = "pk"
    permission_classes = [AllowAny]
    pagination_class = CustomPagination


class BankAccountViewSet(RetrieveModelMixin, UpdateModelMixin, ListModelMixin, GenericViewSet):
    """
    Viewset for performing CRUD operations on user bank accounts.
    """

    queryset = UserBankAccount.objects.all()
    serializer_class = UserBankAccountSerializer
    lookup_field = "pk"
    permission_classes = [IsOwnerOrStaff, IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination  # Assuming CustomPagination is defined in your code

    def get_queryset(self) -> QuerySet:
        """
        Override the queryset to filter based on user ownership or staff status.
        """
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_staff:
            return queryset  # Staff can view all bank accounts

        return queryset.filter(user=user)

    @action(detail=False)
    def details(self, request):
        try:
            # Use the queryset directly to get the user's bank account instance
            bank_account_instance = UserBankAccount.objects.get(user=request.user)

            # Serialize the user's bank account instance
            serializer = UserBankAccountSerializer(bank_account_instance, context={"request": request})

            # Return a success response with the serialized data and a message
            return Response(
                status=status.HTTP_200_OK,
                data={"message": "User bank account details fetched successfully", "data": serializer.data},
            )
        except UserBankAccount.DoesNotExist:
            # Return a not found response if the user's bank account instance does not exist
            return Response(status=status.HTTP_404_NOT_FOUND, data={"message": "User bank account details not found"})
        except Exception as e:
            # Return a bad request response with an error message
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": f"There was an error fetching the user bank account details. {str(e)}"},
            )

    def update(self, request, *args, **kwargs):
        """
        Custom update method to return a response with a success message.

        Args:
        - request: The DRF request object.

        Returns:
        - Response: The DRF response object with a success message.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(
                data={"message": "User bank account details updated successfully"}, status=status.HTTP_200_OK
            )
        except UserBankAccount.DoesNotExist:
            # Return a not found response if the user's bank account instance does not exist
            return Response(status=status.HTTP_404_NOT_FOUND, data={"message": "User bank account details not found"})
        except Exception as e:
            # Return a bad request response with an error message
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": f"There was an error updating your bank details. {str(e)}"},
            )

    def list(self, request, *args, **kwargs):
        """
        Custom list method to return a simplified response with the list of user bank accounts.

        Args:
        - request: The DRF request object.

        Returns:
        - Response: The DRF response object with the list of user bank accounts.
        """
        try:
            user_bank_accounts = self.get_queryset()
            serialized_bank_accounts = self.get_serializer(user_bank_accounts, many=True).data

            return Response(
                data={"message": "List of user bank accounts fetched successfully", "data": serialized_bank_accounts},
                status=status.HTTP_200_OK,
            )
        except UserBankAccount.DoesNotExist:
            # Return a not found response if the user's bank account instance does not exist
            return Response(status=status.HTTP_404_NOT_FOUND, data={"message": "User bank accounts details not found"})
        except Exception as e:
            # Return a bad request response with an error message
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": f"There was an error fectching the users your bank details. {str(e)}"},
            )


class EarningViewSet(RetrieveModelMixin, UpdateModelMixin, ListModelMixin, GenericViewSet):
    queryset = UserEarning.objects.all()
    serializer_class = UserEarningSerializer
    lookup_field = "pk"
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Custom update method to return a response with a success message.

        Args:
        - request: The DRF request object.

        Returns:
        - Response: The DRF response object with a success message.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(data={"message": "User earnings details updated successfully"}, status=status.HTTP_200_OK)

        except UserEarning.DoesNotExist:
            # Return a not found response if the user's earnings instance does not exist
            return Response(status=status.HTTP_404_NOT_FOUND, data={"message": "User earnings details not found"})

        except Exception as e:
            # Return a bad request response with an error message
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": f"There was an error updating your earnings details. {str(e)}"},
            )

    @action(detail=False)
    def balance(self, request):
        """
        Custom action to retrieve the user's earnings balance.

        Args:
        - request: The DRF request object.

        Returns:
        - Response: The DRF response object with the serialized earnings balance and a success message.
        """
        try:
            # Use the queryset directly to get the user's earnings instance
            user_earning_instance = UserEarning.objects.get(user=request.user)

            # Serialize the user's earnings instance
            serializer = UserEarningSerializer(user_earning_instance, context={"request": request})

            # Return a success response with the serialized data and a message
            return Response(
                status=status.HTTP_200_OK,
                data={"message": "User balance fetched successfully", "data": serializer.data},
            )

        except UserEarning.DoesNotExist:
            # Return a not found response if the user's earnings instance does not exist
            return Response(status=status.HTTP_404_NOT_FOUND, data={"message": "User balance not found"})

        except Exception as e:
            # Return a bad request response with an error message
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": f"There was an error fetching the user balance. {str(e)}"},
            )
