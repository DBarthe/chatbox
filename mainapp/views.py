from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from django.utils.translation import npgettext
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from .models import Message

class Index(TemplateView):

  template_name = 'mainapp/index.html'

  def get_context_data(self, **kwargs):
    context = super(Index, self).get_context_data(**kwargs)
    context['blabla'] = "hello"
    return context

class FetchMessagesBase(View):

  def prepare_message(self, message):
    return {
      'id': message.id,
      'datetime': message.datetime,
      'author': message.author_pseudo,
      'content': message.content,
    }

  def prepare_message_list(self, message_list):
    return [ self.prepare_message(message) for message in message_list]

  def make_resp_data(self, message_list):
    return {
      'data': self.prepare_message_list(message_list)
    }

class FetchMessagesSince(FetchMessagesBase):
  """ Return all messages posted since one particular message """

  def get(self, request, *args, **kwargs):
    try:
      message_id = int(request.GET['message_id'])
      message_list = Message.objects.filter(id__gt=message_id)
      resp_data = self.make_resp_data(message_list)
      return JsonResponse(resp_data)

    except KeyError:
      return HttpResponseBadRequest("Missing required parameter 'message_id'", content_type="text/plain")
    except ValueError:
      return HttpResponseBadRequest("Parameter 'message_id' was not a valid integer", content_type="text/plain")


class FetchAllMessages(FetchMessagesBase):

  def get(self, request, *args, **kwargs):
    message_list = Message.objects.all()
    resp_data = self.make_resp_data(message_list)
    return JsonResponse(resp_data)

class FetchLastMessages(FetchMessagesBase):
  DEFAULT_MESSAGE_COUNT = 20

  def get(self, request, *args, **kwargs):
    try:
      count = int(request.GET.get('count', FetchLastMessages.DEFAULT_MESSAGE_COUNT))
      if count < 0:
        return HttpResponseBadRequest("Parameter 'count' was nagative", content_type="text/plain")
      else:
        message_list = Message.objects.order_by('-id')[:count]
        message_list.reverse()
        resp_data = self.make_resp_data(message_list)
        return JsonResponse(resp_data)

    except ValueError:
      return HttpResponseBadRequest("Parameter 'count' was not a valid integer", content_type="text/plain")


from django.core.management.base import NoArgsCommand


class PushMessage(View):

  def get(self, request, *args, **kwargs):
    request.POST = request.GET
    return self.post(request)

  def post(self, request, *args, **kwargs):

    try:
      author_ip = request.META['REMOTE_ADDR']
      author_pseudo = request.POST['pseudo']
      message_content = request.POST['content']

      message = Message(author_ip=author_ip, author_pseudo=author_pseudo, content=message_content)
      message.save()

      response = HttpResponse("The message has been sent", content_type="text/plain")
      response.status_code = 201
      return response

    except KeyError as e:
      return HttpResponseBadRequest("Parameter " + e.args[0] + " was missing'", content_type="text/plain")