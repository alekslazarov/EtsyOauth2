from django.views.generic.base import TemplateView


class Oauth2View(TemplateView):
    template_name = 'oauth2.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['access_token'] = self.request.session.get('access_token', '')
        context['refresh_token'] = self.request.session.get('refresh_token', '')
        context['error'] = self.request.session.get('error', '')
        self.request.session['error'] = ''

        return context
