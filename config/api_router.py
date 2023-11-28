from dj_rest_auth.registration.views import VerifyEmailView
from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from iwitness_be.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet, basename="users")


app_name = "api"
urlpatterns = router.urls

urlpatterns += [
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path("auth/account-confirm-email/", VerifyEmailView.as_view(), name="account_email_verification_sent"),
]
