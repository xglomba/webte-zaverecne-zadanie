from django.views.i18n import set_language


def change_language(request):
    return set_language(request)
