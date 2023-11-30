from __future__ import annotations

from allauth.account.models import EmailAddress
from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateField,
    EmailField,
    FileField,
    ForeignKey,
    GenericIPAddressField,
    ManyToManyField,
    OneToOneField,
    TextField,
)
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from model_utils import FieldTracker
from model_utils.models import TimeStampedModel

from iwitness_be.users.managers import UserManager
from iwitness_be.utils.validators import validate_uploaded_image_extension


class User(AbstractUser):
    """
    Custom user model for the iwitness-reporter-be application.

    This model extends the default Django AbstractUser model to include additional
    fields and properties for user management and profile tracking.

    Attributes:
    - name (str): The name of the user (optional).
    - email (str): The unique email address of the user.
    - verified (bool): Indicates whether the user's email is verified.
    - user_ip (str): The IP address of the user (optional).
    - followers (ManyToManyField): Relationship with other users who are followers.
    - tracker (FieldTracker): Tracks changes in specified fields.

    Properties:
    - is_email_verified (bool): Checks if the user's email is verified.
    - user_token (str): Retrieves the authentication token for the user.

    Methods:
    - get_absolute_url(): Generates the URL for the user's detail view.

    Meta:
    - managed (bool): Indicates whether this model is managed by Django.
    - verbose_name (str): Human-readable singular name for the model.
    - verbose_name_plural (str): Human-readable plural name for the model.
    - ordering (list): Default ordering for the model records based on date joined.
    """

    name = CharField(_("Name of User"), blank=True, max_length=255)
    email = EmailField(_("email address"), unique=True)
    verified = BooleanField(default=False)
    user_ip = GenericIPAddressField(null=True, blank=True)
    followers = ManyToManyField("self", symmetrical=False, through="UserFollow", related_name="following")
    tracker = FieldTracker(fields=["user_ip"])

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def is_email_verified(self):
        """
        Check if the user's email is verified.

        Returns:
        - bool: True if the email is verified, False otherwise.
        """
        try:
            email_address = EmailAddress.objects.get_for_user(self, self.email)
            return email_address.verified
        except EmailAddress.DoesNotExist:
            return False

    @property
    def user_token(self):
        """
        Get the authentication token for the user.

        Returns:
        - str or None: The authentication token if it exists, otherwise None.
        """
        try:
            return self.auth_token.key
        except AttributeError:
            return None

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.
        """
        return reverse("users:detail", kwargs={"username": self.username})

    class Meta:
        verbose_name = "User Account"
        verbose_name_plural = "Users Account"
        ordering = ["-date_joined"]


class UserFollow(TimeStampedModel):
    """
    Model for tracking user follows.
    """

    following = ForeignKey(User, on_delete=CASCADE, related_name="user_following")
    follower = ForeignKey(User, on_delete=CASCADE, related_name="user_followers")

    def __str__(self):
        return f"Following information for {self.user.username}"

    class Meta:
        unique_together = ("follower", "following")
        verbose_name = "User Follow"
        verbose_name_plural = "Users Follow"
        ordering = ["-created"]


class Profile(TimeStampedModel):
    """
    Model to store relative information about a user in their profile.

    Attributes:
    - user: The associated User instance.
    - image: Profile photo of the user.
    - date_of_birth: Date of birth of the user.
    - bio: Short introduction of the user.
    - gender: Gender of the user, selected from predefined choices (Male, Female, None).

    Methods:
    - __str__: Returns a string representation of the model instance.

    Meta:
    - verbose_name: Singular name for the model in the admin interface.
    - verbose_name_plural: Plural name for the model in the admin interface.
    - ordering: Default ordering of instances based on creation time.
    """

    MALE = "M"
    FEMALE = "F"
    NONE = "B"
    GENDER = ((MALE, _("Male")), (FEMALE, _("Female")), (NONE, _("None")))

    user = OneToOneField(User, on_delete=CASCADE, related_name="user_profile", db_index=True)
    image = FileField(_("Profile Photo"), upload_to="profile", validators=[validate_uploaded_image_extension])
    date_of_birth = DateField(_("Date of Birth"), blank=True, null=True)
    bio = TextField(_("Write a short introduction of yourself"))
    gender = CharField(max_length=3, choices=GENDER, default=NONE)

    def __str__(self):
        """
        String representation of the Profile instance.

        Returns:
        - str: String representation.
        """
        return f"Profile for {self.user.username}"

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("Users Profile")
        ordering = ["-created"]


class UserPrivacyConsent(TimeStampedModel):
    """
    Model for tracking user privacy consents.

    Attributes:
    - user: The associated User instance.
    - of_legal_age: Boolean field indicating if the user is of legal age.
    - ip_address: IP address of the user when consent was given.
    - user_agent: User agent information of the browser when consent was given.
    - data_collection: Boolean field indicating user consent for data collection.
    - marketing_emails: Boolean field indicating user consent for receiving marketing emails.
    - third_party_services: Boolean field indicating user consent for the use of third-party services.

    Methods:
    - __str__: Returns a string representation of the model instance.

    Meta:
    - verbose_name: Singular name for the model in the admin interface.
    - verbose_name_plural: Plural name for the model in the admin interface.
    - ordering: Default ordering of instances based on creation time.
    """

    user = OneToOneField(User, on_delete=CASCADE, related_name="user_privacy_consent")
    of_legal_age = BooleanField(default=True)
    ip_address = GenericIPAddressField(null=True, blank=True)
    user_agent = TextField(null=True, blank=True)
    data_collection = BooleanField(default=False)
    marketing_emails = BooleanField(default=False)
    third_party_services = BooleanField(default=False)

    def __str__(self):
        """
        String representation of the UserPrivacyConsent instance.

        Returns:
        - str: String representation.
        """
        return f"Privacy Consents for {self.user.username}"

    class Meta:
        verbose_name = "User Privacy Consent"
        verbose_name_plural = "User Privacy Consents"
        ordering = ["-created"]


class UserLocation(TimeStampedModel):
    """
    Model to store location information about a user.

    Attributes:
    - user: The associated User instance.
    - town: Town of the user's location.
    - state: State of the user's location.
    - country: Country of the user's location.
    - tracker: FieldTracker to keep track of changes in 'town', 'state', and 'country'.

    Properties:
    - full_address: Combines town, state, and country to form a complete address.

    Methods:
    - __str__: Returns a string representation of the model instance.

    Meta:
    - verbose_name: Singular name for the model in the admin interface.
    - verbose_name_plural: Plural name for the model in the admin interface.
    - ordering: Default ordering of instances based on creation time.
    """

    user = OneToOneField(User, on_delete=CASCADE, related_name="user_location", db_index=True)
    town = CharField(max_length=50, blank=True)
    state = CharField(max_length=50, blank=True)
    country = CharField(max_length=50, blank=True)
    tracker = FieldTracker(fields=["town", "state", "country"])

    def __str__(self):
        """
        String representation of the UserLocation instance.

        Returns:
        - str: String representation.
        """
        return f"Locations for {self.user.username}"

    @property
    def full_address(self):
        """
        Combines town, state, and country to form a complete address.

        Returns:
        - str: Combined address.
        """
        address_components = filter(None, [self.town, self.state, self.country])
        return ", ".join(address_components)

    class Meta:
        verbose_name = "User Location"
        verbose_name_plural = "User Locations"
        ordering = ["-created"]
