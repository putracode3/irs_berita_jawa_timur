from django.conf import settings
from django.db import models

from django.urls import reverse

# Create your models here.


class Post(models.Model):
  title = models.CharField(max_length=200)
  # Slug, ini untuk membangun URL agar terlihat indah atau bisa dibaca.s
  slug = models.SlugField(unique=True)
  image = models.ImageField(upload_to='post/%Y/%m', blank=True)
  content = models.TextField()
  draft = models.BooleanField(default=False)
  publish = models.DateField(auto_now=False, auto_now_add=False)
  updated = models.DateTimeField(auto_now=True, auto_now_add=False)
  timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
  objects = models.Manager()

  def __str__(self):
    return self.title

  def get_absolute_url(self):
    return reverse('posts:detail', kwargs={"slug": self.slug})
