from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
  lessons = models.ManyToManyField("Lesson")

class Language(models.Model):
  name = models.CharField(default="python", max_length=255)

  def __str__(self):
    return self.name

DEFAULT_LANGUAGE_ID = 1
class Lesson(models.Model):
  owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  language = models.ForeignKey(Language, on_delete=models.CASCADE, default=DEFAULT_LANGUAGE_ID)
  title = models.CharField(null=True, blank=False, max_length=255)
  content = models.TextField()

  def __str__(self):
    return self.title
