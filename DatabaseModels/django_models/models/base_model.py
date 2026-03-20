from django.db import models


class BaseModel(models.Model):
    is_active = models.BooleanField(null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        abstract = True
