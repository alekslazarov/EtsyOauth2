from django.views.generic.base import TemplateView
from django.conf import settings


class Oauth2View(TemplateView):
    template_name = 'oauth2.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['etsy_api_key'] = settings.ETSY_API_KEY

        return context
