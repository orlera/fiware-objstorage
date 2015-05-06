from django.db import models
from custom_storage import CustomStorage

class Attachment(models.Model):
    name = models.CharField(max_length = 50)
    attachment = models.FileField(upload_to = 'storage', storage=CustomStorage())
    upload_date = models.DateTimeField('upload_date')