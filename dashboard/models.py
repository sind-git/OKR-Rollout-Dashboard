from django.db import models

# Create your models here.
class Functions(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Managers(models.Model):
    functionname = models.ForeignKey(Functions, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def _str_(self):
        return self.name



