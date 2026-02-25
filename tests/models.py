from django.db import models

from django_openutils.mixins import ModelDiffMixin


class TrackedModel(ModelDiffMixin, models.Model):
    name = models.CharField(max_length=100, blank=True, default="")
    value = models.IntegerField(null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "tests"
