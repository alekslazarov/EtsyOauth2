from django.views.generic.base import TemplateView


class Oauth2View(TemplateView):
    template_name = 'oauth2.html'
