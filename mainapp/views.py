from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils.translation import npgettext

class Index(TemplateView):

  template_name = 'mainapp/index.html'

  def get_context_data(self, **kwargs):
    context = super(Index, self).get_context_data(**kwargs)
    context['blabla'] = "hello"
    return context

