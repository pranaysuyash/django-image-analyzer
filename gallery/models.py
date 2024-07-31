from django.db import models

# Create your models here.
class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    tags = models.TextField(blank=True)

    def __str__(self):
        return self.image.name