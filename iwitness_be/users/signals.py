from datetime import date

from allauth.account.adapter import get_adapter
from allauth.account.signals import user_logged_in  # , user_signed_up

# from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save  # , pre_save
from django.dispatch import receiver

from iwitness_be.monetize.models import UserBankAccount, UserEarning
from iwitness_be.users.models import Profile, UserLocation, UserPrivacyConsent
from iwitness_be.utils.email_sender import CustomEmailSender
from iwitness_be.utils.logger import LOGGER

today = date.today()
User = get_user_model()


@receiver(post_save, sender=User)
def create_user_relationships(sender, instance, created, **kwargs):
    """
    Signal handler to create relationships when a new User is created.

    Args:
    - sender: The sender of the signal.
    - instance: The instance of the User model.
    - created: A boolean indicating if the instance was created.
    - kwargs: Additional keyword arguments.

    Returns:
    - None
    """
    if created:
        # If the user is a superuser, mark them as verified
        if instance.is_superuser:
            User.objects.filter(username=instance.username).update(verified=True)

        # Create profile, privacy consent, location, bank account, and earning objects for the user
        Profile.objects.create(user=instance)
        UserPrivacyConsent.objects.create(user=instance)
        UserLocation.objects.create(user=instance)
        UserBankAccount.objects.create(user=instance)
        UserEarning.objects.create(user=instance)

        # Log information about the relationships creation
        LOGGER.info(
            f"""
            [RELATIONSHIP CREATED] The {instance.username} account has been
            created successfully with all relationships attached to the main
            user account"""
        )


@receiver(user_logged_in)
def update_user_ip_on_login(sender, request, user, **kwargs):
    """
    Signal handler to update the user's IP address when they log in.

    Args:
    - sender: The sender of the signal.
    - request: The Django request object.
    - user: The user instance.
    - kwargs: Additional keyword arguments.

    Returns:
    - None
    """
    adapter = get_adapter(request)
    user_ip = adapter.get_client_ip(request)
    user.user_ip = user_ip
    user.save(update_fields=["user_ip"])
    ctx = {"old_ip": user.tracker.previous(user_ip), "new_ip": user_ip, "username": user.username}
    email = user.email
    if (
        user.tracker.has_changed("user_ip")
        and user.tracker.previous("user_ip") != user_ip
        and user.tracker.previous("user_ip") is not None
    ):
        CustomEmailSender.send_mail(template_prefix="emails/new_ip_emails/new_ip_address", email=email, context=ctx)
