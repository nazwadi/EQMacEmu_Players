from django.conf import settings
from django.db import models
from django.urls import reverse
from mdeditor.fields import MDTextField
from django.template.defaultfilters import truncatewords

from django.contrib.auth.models import User

PATCH_TYPE_CHOICES = [
    ('patch', 'Patch'),
    ('hotfix', 'Hotfix'),
    ('press_release', 'Press Release'),
    ('news', 'News'),
]

EXPANSION_CHOICES = [
    ('classic',   'Classic'),
    ('kunark',    'Ruins of Kunark'),
    ('velious',   'Scars of Velious'),
    ('luclin',    'Shadows of Luclin'),
    ('pop',       'Planes of Power'),
    ('ykesha',    'Legacy of Ykesha'),
    ('ldon',      'Lost Dungeons of Norrath'),
    ('gates',     'Gates of Discord'),
    ('omens',     'Omens of War'),
    ('dragons',   'Dragons of Norrath'),
    ('dod',       'Depths of Darkhollow'),
    ('por',       'Prophecy of Ro'),
    ('tss',       "The Serpent's Spine"),
    ('tbs',       'The Buried Sea'),
    ('sof',       'Secrets of Faydwer'),
    ('sod',       'Seeds of Destruction'),
    ('underfoot', 'Underfoot'),
    ('hot',       'House of Thule'),
]

class PatchMessage(models.Model):
    title = models.CharField(max_length=255, unique=True)
    body_markdown = MDTextField()
    body_plaintext = models.TextField(blank=True, null=True)
    patch_date = models.DateTimeField(null=False)
    patch_number_this_date = models.IntegerField(null=False, default=1) # sometimes there is more than one patch in a day
    patch_year = models.IntegerField(null=False, default=1999)
    patch_type = models.CharField(max_length=20, choices=PATCH_TYPE_CHOICES, default='patch')
    expansion = models.CharField(max_length=20, choices=EXPANSION_CHOICES, blank=True, null=True)
    markdown_edited = models.BooleanField(default=False)
    tags = models.ManyToManyField('PatchTag', blank=True, related_name='patches')
    source_notes = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, null=False, unique=True)

    class Meta:
        indexes = [
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
    subject = models.CharField(max_length=255, blank=True, default='')
    body = MDTextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.username)


class PatchTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name