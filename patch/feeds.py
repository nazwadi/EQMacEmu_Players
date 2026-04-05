from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import PatchMessage


class LatestPatchesFeed(Feed):
    title = "EverQuest Patch Archive"
    description = "EverQuest live server patch messages, 1999–2010"

    def link(self):
        return reverse('patch:index')

    def items(self):
        return PatchMessage.objects.order_by('-patch_date', '-patch_number_this_date')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return (item.body_plaintext or '')[:500]

    def item_pubdate(self, item):
        return item.patch_date

    def item_link(self, item):
        return reverse('patch:view', kwargs={'slug': item.slug})
