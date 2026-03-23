from django.views.generic import TemplateView


class FrontendView(TemplateView):
    """
    View для отображения фронтенда.

    Возвращает index.html для всех маршрутов, не соответствующих API.
    """
    template_name = 'index.html'