from django.conf import settings


def adsense(request):
    return {"ADSENSE_ID": getattr(settings, "ADSENSE_ID", "")}
