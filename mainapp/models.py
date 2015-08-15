from django.db import models
from django.utils.translation import ugettext_lazy as _

class Message(models.Model):

  # the implicit id is used to determine message order
  author_pseudo = models.CharField(max_length=64, blank=False, verbose_name=_("author's pseudo"))

  author_ip = models.GenericIPAddressField(null=True, verbose_name=_("author's ip address"))

  content = models.TextField(verbose_name=_('message content'))

  datetime = models.DateTimeField(auto_now_add=True, verbose_name=_("date and time"),
    help_text=_("the datetime of the message creation"))

  def __str__(self):
    return self.author_pseudo + ': ' + self.content
