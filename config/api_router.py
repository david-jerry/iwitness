from dj_rest_auth.registration.views import ResendEmailVerificationView, VerifyEmailView
from dj_rest_auth.views import PasswordResetConfirmView, PasswordResetView
from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from iwitness_be.users.api.views import UserViewSet
from iwitness_be.users.views import email_confirm_redirect, password_reset_confirm_redirect

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet, basename="users")

app_name = "api"
urlpatterns = router.urls

urlpatterns += [
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/verify-email/", VerifyEmailView.as_view(), name="account_verify_email"),
    path(
        "auth/registration/account-resend-email/",
        ResendEmailVerificationView.as_view(),
        name="account_email_resend_verification",
    ),
    path("auth/registration/account-confirm-email/<str:key>/", email_confirm_redirect, name="account_confirm_email"),
    path(
        "auth/registration/account-confirm-email/", VerifyEmailView.as_view(), name="account_email_verification_sent"
    ),
    # path(
    #     "auth/registration/account-confirm-email/<str:key>/", ConfirmEmailView.as_view()
    # ),  # Needs to be defined before the registration path
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path("auth/password/reset/", PasswordResetView.as_view(), name="account_password_reset"),
    path(
        "auth/password/reset/confirm/<str:uidb64>/<str:token>/",
        password_reset_confirm_redirect,
        name="password_reset_confirm",
    ),
    path("auth/password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]
