#!/usr/bin/env python3
"""The module defines the structure of the models Django."""
from django.db import models


class UserImage(models.Model):
    """A model for linking the user and the image of the docker."""
    user_id = models.PositiveIntegerField(verbose_name="User ID")
    image_id = models.CharField(max_length=71, verbose_name="Docker image ID")
    created = models.DateTimeField(verbose_name="Created")
    size = models.PositiveIntegerField(verbose_name="Size")
