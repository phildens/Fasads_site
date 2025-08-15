from django.core.cache import cache
from shop_part.models import Questions

def faq_questions(request):
    cache_key = "faq_questions_all"
    qs = cache.get(cache_key)
    if qs is None:
        qs = list(Questions.objects.all().order_by("id").only("id", "name", "description"))
        cache.set(cache_key, qs, 300)
    return {"questions": qs}
