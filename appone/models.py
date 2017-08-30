from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Asset(models.Model):
    ip = models.CharField(max_length=50)
    cpucore = models.IntegerField(null=True)

    def __str__(self):
        return self.ip

