from django.db import models


class Bond(models.Model):
    isin = models.CharField(max_length=12)
    size = models.BigIntegerField()
    currency = models.CharField(max_length=5)
    maturity = models.DateField()
    lei = models.CharField(max_length=20)
    legal_name = models.CharField(max_length=50)
