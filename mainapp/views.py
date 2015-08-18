from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from django.utils.translation import npgettext
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils import timezone
import pytz


from .models import Message

class Index(TemplateView):

  template_name = 'mainapp/index.html'

  def get(self, request, *args, **kwargs):
    self.set_pseudo = request.GET.get('pseudo', None)

    self.set_tz = request.GET.get('tz', None)
    if self.set_tz is not None:
      try:
        timezone.activate(self.set_tz)
      except pytz.exceptions.UnknownTimeZoneError:
        self.set_tz = None

    return super(Index, self).get(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(Index, self).get_context_data(**kwargs)
    if self.set_pseudo is not None:
      context['pseudo'] = self.set_pseudo
    if self.set_tz is not None:
      context['tz'] = self.set_tz
    return context

class FetchMessagesBase(View):

  def select_timezone_from_request(self, request):
    if request.GET is not None:
      try:
        tz = request.GET['tz']
        timezone.activate(tz)
      except KeyError:
        pass
      except pytz.exceptions.UnknownTimeZoneError:
        pass

  def prepare_message(self, message):
    return {
      'id': message.id,
      'datetime': timezone.localtime(message.datetime).strftime("%X"),
      'author': message.author_pseudo,
      'content': message.content,
    }

  def prepare_message_list(self, message_list):
    return [ self.prepare_message(message) for message in message_list]

  def make_resp_data(self, message_list):
    return {
      'list': self.prepare_message_list(message_list)
    }

class FetchMessagesSince(FetchMessagesBase):
  """ Return all messages posted since one particular message """

  def get(self, request, *args, **kwargs):
    self.select_timezone_from_request(request)
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
    self.select_timezone_from_request(request)
    message_list = Message.objects.all()
    resp_data = self.make_resp_data(message_list)
    return JsonResponse(resp_data)

class FetchLastMessages(FetchMessagesBase):
  DEFAULT_MESSAGE_COUNT = 20

  def get(self, request, *args, **kwargs):
    self.select_timezone_from_request(request)
    try:
      count = int(request.GET.get('count', FetchLastMessages.DEFAULT_MESSAGE_COUNT))
      if count < 0:
        return HttpResponseBadRequest("Parameter 'count' was nagative", content_type="text/plain")
      else:
        message_list = [ m for m in Message.objects.order_by('-id')[:count]]
        message_list.reverse()
        resp_data = self.make_resp_data(message_list)
        return JsonResponse(resp_data)

    except ValueError:
      return HttpResponseBadRequest("Parameter 'count' was not a valid integer " + request.GET.get('count', FetchLastMessages.DEFAULT_MESSAGE_COUNT), content_type="text/plain")


class PushMessage(View):

  def get(self, request, *args, **kwargs):
    request.POST = request.GET
    return self.post(request)

  def post(self, request, *args, **kwargs):

    try:
      author_ip = request.META['REMOTE_ADDR']
      author_pseudo = request.POST['author']
      message_content = request.POST['content']

      if len(author_pseudo) == 0:
        return HttpResponseBadRequest("Parameter 'author' was empty'", content_type="text/plain")
      elif len(message_content) == 0:
        return HttpResponseBadRequest("Parameter 'content' was empty'", content_type="text/plain")

      message = Message(author_ip=author_ip, author_pseudo=author_pseudo, content=message_content)
      message.save()

      response = HttpResponse("The message has been sent", content_type="text/plain")
      response.status_code = 201
      return response

    except KeyError as e:
      return HttpResponseBadRequest("Parameter " + e.args[0] + " was missing'", content_type="text/plain")