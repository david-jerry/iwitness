from django.contrib.auth import get_user_model
from django.db.models import CASCADE, BooleanField, CharField, DecimalField, ForeignKey, OneToOneField, SlugField
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

User = get_user_model()


# Create your models here.
class Banks(TimeStampedModel):
    """Supported banks from paystack

    Args:
        TimeStampedModel (AbstractModel): to represent Created(DateTimeField) and Modified(DateTimeField - Auto)
    """

    name = CharField(max_length=500, unique=True)
    slug = SlugField(unique=True)
    lcode = CharField(max_length=25, db_index=True)
    code = CharField(max_length=10, db_index=True)
    country_iso = CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Bank")
        verbose_name_plural = _("Banks")
        ordering = ["name"]


class UserBankAccount(TimeStampedModel):
    """
    Model to store bank account information for users.
    """

    user = OneToOneField(User, on_delete=CASCADE, related_name="user_bank", db_index=True)
    verified = BooleanField(default=False, help_text=_("Indicates whether the bank account is verified."))
    bank = ForeignKey(Banks, on_delete=CASCADE, related_name="bank_name")
    account_name = CharField(max_length=255, blank=True, help_text=_("Name associated with the bank account."))
    account_number = CharField(
        max_length=16, blank=True, unique=True, db_index=True, help_text=_("Bank account number.")
    )

    def __str__(self):
        return f"Bank Account for {self.user.username}"

    class Meta:
        verbose_name = _("User Bank Account")
        verbose_name_plural = _("Users Bank Account")
        ordering = ["-created"]  # Order by creation timestamp in descending order.


class UserEarning(TimeStampedModel):
    """
    Model to store user earnings information.
    """

    user = OneToOneField(User, on_delete=CASCADE, related_name="user_earning", db_index=True)
    balance = DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text=_("Current balance of the user's earnings.")
    )

    def __str__(self):
        return f"Earnings for {self.user.username}"

    class Meta:
        verbose_name = _("User Earning")
        verbose_name_plural = _("Users Earning")
        ordering = ["-modified"]  # Order by creation timestamp in descending order.
