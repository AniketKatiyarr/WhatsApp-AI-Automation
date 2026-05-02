from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user: each user represents one business for MVP.

    Important: api_key and whatsapp_token are sensitive. In production you should
    store them encrypted (KMS / field-level encryption) and scope outbound API usage.
    """

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    business_name = models.CharField(max_length=255, blank=True, default="")
    business_type = models.CharField(max_length=255, blank=True, default="business")

    api_key = models.CharField(max_length=255, blank=True, default="")
    whatsapp_token = models.CharField(max_length=512, blank=True, default="")
    whatsapp_phone_number_id = models.CharField(max_length=128, blank=True, default="")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.business_name or 'Business'})"

