from django import template
from articles.models import Article

register = template.Library()

@register.inclusion_tag("articles/partials/slider.html", takes_context=True)
def articles_slider(context, limit=20, exclude_slug=None, autoplay=True, interval=4000):
    qs = Article.objects.filter(status=Article.Status.PUBLISHED).order_by("-published_at")
    if exclude_slug:
        qs = qs.exclude(slug=exclude_slug)
    # limit=0 или None -> все статьи
    if limit and int(limit) > 0:
        qs = qs[:int(limit)]
    return {
        "items": qs,
        # пробрасываем параметры в partial через data-атрибуты
        "slider_attrs": {
            "autoplay": "true" if autoplay else "false",
            "interval": str(int(interval)),
        },
    }
