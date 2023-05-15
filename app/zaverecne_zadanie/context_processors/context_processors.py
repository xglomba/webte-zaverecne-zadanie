from app.settings import LANGUAGES


def trans_context(request):
    current_path = request.get_full_path()
    if current_path.startswith(("/sk", "/en")):
        current_path = current_path[3:]
    lang_links = [lang[0] for lang in LANGUAGES]

    return {'lang_links': lang_links, 'current_path': current_path}
