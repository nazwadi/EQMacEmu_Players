from django.conf import settings
from django.db import models
from django.urls import reverse
from mdeditor.fields import MDTextField
from django.template.defaultfilters import truncatewords

from django.contrib.auth.models import User

class PatchMessage(models.Model):
    title = models.CharField(max_length=255, unique=True)
    body_markdown = models.TextField()
    body_plaintext = models.TextField(blank=True, null=True)
    patch_date = models.DateTimeField(null=False)
    patch_number_this_date = models.IntegerField(null=False, default=1) # sometimes there is more than one patch in a day
    patch_year = models.IntegerField(null=False, default=1999)
    source_notes = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, null=False, unique=True)

    indexes = [
        models.Index(fields=['title']),
        models.Index(fields=['body_plaintext']),
        models.Index(fields=['patch_year']),
        models.Index(fields=['patch_date']),
    ]

    @property
    def short_description(self):
        return truncatewords(self.body_plaintext, 20)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('patch:view', kwargs={'slug': self.slug})

class Comment(models.Model):
    patch_message = models.ForeignKey(PatchMessage,on_delete=models.CASCADE,related_name='comments')
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='comments')
    subject = models.CharField(max_length=255, null=False, blank=False)
    body = MDTextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.username)