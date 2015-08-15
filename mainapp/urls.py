from django.conf.urls import url

from .views import Index, FetchMessagesSince, FetchAllMessages, FetchLastMessages, PushMessage

urlpatterns = [
  url(r'^$', Index.as_view(), name='index'),
  url(r'^fetch/since$', FetchMessagesSince.as_view(), name='fetch_messages_since'),
  url(r'^fetch/all$', FetchAllMessages.as_view(), name='fetch_all_messages'),
  url(r'^fetch/last$', FetchLastMessages.as_view(), name='fetch_last_messages'),
  url(r'^push$', PushMessage.as_view(), name='push_message'),
]
