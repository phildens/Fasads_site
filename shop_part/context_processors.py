from django.core.cache import cache
from shop_part.models import Questions


def faq_questions(request):
    cache_key = "faq_questions_all"
    qs = cache.get(cache_key)
    if qs is None:
        qs = list(Questions.objects.all().order_by("id").only("id", "name", "description"))
        cache.set(cache_key, qs, 300)
    return {"questions": qs}


from django.core.cache import cache
from .models import SiteSettings


def site_settings(request):
    cache_key = "site_settings_singleton"
    data = cache.get(cache_key)
    if data is None:
        s = SiteSettings.load()
        data = {
            "email": s.email or "",
            "phone": s.phone or "",
            "phone_href": s.phone_href or "",
        }
        cache.set(cache_key, data, 300)  # 5 минут
    return {"site_settings": data}
