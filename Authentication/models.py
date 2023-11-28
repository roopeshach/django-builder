
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

def image_size_validator(value):
    max_size = 10485760

    if value.size > max_size:
        raise ValidationError(f"Image must be less than 10MB")

class ApplicationUser(AbstractUser):
    profile_pic = models.ImageField(upload_to='profile_pictures', blank=True, null=True, validators=[image_size_validator, FileExtensionValidator(allowed_extensions=['jpeg', 'png', 'gif'])])
    contact = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
