from django.shortcuts import render
from shop_part.models import Product
from shop_part.serializers import ProductSerializer, ProductInCatSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from shop_part.models import Category, Product, TypeMaterial, Questions
from django.http import JsonResponse
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import ContactRequest
from shop_part.models import Category, Product, TypeMaterial, Questions
from django.shortcuts import render
from .models import BigGalery
from django.http import Http404
from django.db.models import Count
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, Category, FilterKey
from .serializers import ProductInCatSerializer, ProductSerializer, \
    ProductDetailSerializer  # или твой detail serializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# views.py
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Product  # проверь импорт


class SimilarProductsAPIView(APIView):
    """
    GET /api/products/<int:pk>/similar/?limit=8
    Возвращает [{id, name, card_image}] по той же категории.
    """

    def get(self, request, pk: int):
        limit = int(request.GET.get("limit", 8))
        base = get_object_or_404(Product, pk=pk)
        qs = (Product.objects
              .filter(category=base.category)
              .exclude(id=base.id)
              .order_by("-id")[:limit])
        ser = ProductInCatSerializer(qs, many=True, context={"request": request})
        return Response({"items": ser.data})


# --- Страница с результатами: используем твой catalog.html ---
def product_search(request):
    q = (request.GET.get("q") or "").strip()

    context = {
        # catalog.html узнает, что мы в режиме поиска
        "category_slug": "search",
        "search_query": q,
        # если у тебя слева фильтры — их можно скрыть флагом
        "hide_filters": True,
    }
    return render(request, "catalog.html", context)


# --- API: мета категории "search" (фронту достаточно минимума) ---
def api_search_category_meta(request):
    return JsonResponse({
        "slug": "search",
        "name": "Поиск",
        "filtersEnabled": False,  # говорим фронту, что фильтров нет
    })


# --- API: фильтры для "search" (пусто) ---
def api_search_filters(request):
    return JsonResponse({
        "groups": []  # пустой список групп, чтобы JS не падал
    })


# --- API: товары для "search" ---
def api_search_products(request):
    q = (request.GET.get("q") or "").strip()

    qs = (
        Product.objects.all()
        .select_related(
            "manufacturer", "category", "color",
            "product_type", "type_material",
            "frosen_defend", "strength_grade", "water_resistance",
        )
        .prefetch_related("images", "formats", "emptiness")
    )

    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(manufacturer__name__icontains=q) |
            Q(category__name__icontains=q) |
            Q(color__name__icontains=q) |
            Q(product_type__name__icontains=q) |
            Q(type_material__name__icontains=q) |
            Q(frosen_defend__name__icontains=q) |
            Q(strength_grade__name__icontains=q) |
            Q(water_resistance__name__icontains=q) |
            Q(formats__name__icontains=q) |
            Q(emptiness__name__icontains=q)
        ).distinct()
    else:
        # без запроса возвращаем пусто, чтобы не грузить всё подряд
        qs = qs.none()

    qs = qs.order_by("-id")

    # пагинация
    page = request.GET.get("page", 1)
    per_page = int(request.GET.get("per_page", 12))
    paginator = Paginator(qs, per_page)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Сериализация под карточки (минимально: id, name, image, link)
    items = []
    for p in page_obj.object_list:
        items.append({
            "id": p.id,
            "name": p.name,
            "card_image": (p.card_image.url if getattr(p, "card_image", None) else None),
            "link": reverse("product_client_view", args=[p.pk]),  # путь на детальную
        })

    return JsonResponse({
        "items": items,
        "page": page_obj.number,
        "pages": paginator.num_pages,
        "has_next": page_obj.has_next(),
        "has_prev": page_obj.has_previous(),
        "total": paginator.count,
        "query": q,
    })


def galery(request):
    # та самая коллекция карточек — сортируем по position и сразу подтягиваем связанные SmallGallery
    items = BigGalery.objects.filter(our_supplies=True).order_by('position').prefetch_related('images')
    not_supplies = BigGalery.objects.exclude(our_supplies=True).order_by('position')
    print(not_supplies)
    return render(request, 'galery.html', {
        'items': items,
        'not_supplies': not_supplies,
    })


# Create your views here.
class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


def index(request):
    return render(request, 'index.html')


def yandex_find(request):
    return render(request, 'yandex_94334ec1e6b86559.html')


def products(request):
    return render(request, 'category.html')


def category(request):
    cat_id = Category.objects.get(link_name=request.GET.get('cat_name'))
    products = Product.objects.filter(category=cat_id)
    products = ProductInCatSerializer(products, many=True, context={'request': request})
    print(products.data[0])
    return render(request, 'category.html', {'products': products.data, 'cat_name': ["Главная", cat_id.name],
                                             'questions': Questions.objects.all()})


def about(request):
    return render(request, 'about.html')


def privacy(request):
    return render(request, 'privacy.html')


class FAQView(ListView):
    model = Questions
    template_name = "accordion.html"  # см. файл ниже
    context_object_name = "questions"
    queryset = Questions.objects.all().order_by("id")


@require_POST
def contact_request_create(request):
    # простая валидация
    data = request.POST
    # Маппинг: принимаем и "старые" и ваши имена полей
    first_name = (data.get("first_name") or data.get("name") or "").strip()
    last_name = (data.get("last_name") or data.get("surname") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    description = (data.get("description") or data.get("about") or "").strip()

    errors = {}
    if not first_name:
        errors["first_name"] = ["Обязательное поле."]
    if not email:
        errors["email"] = ["Обязательное поле."]
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = ["Некорректный email."]

    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    ContactRequest.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        description=description,
    )
    return JsonResponse({"ok": True})


from rest_framework.generics import get_object_or_404

from .models import Category
from .serializers import CategorySerializer


class CategoryDetailAPIView(APIView):
    """
    GET /api/categories/<category_key>/
    Ищет категорию по link_name (slug-подобное), name или id.
    """

    def get(self, request, category_key: str):
        lookup = (category_key or "").strip()
        cond = Q(link_name__iexact=lookup) | Q(name__iexact=lookup)
        if lookup.isdigit():
            cond |= Q(id=int(lookup))
        obj = get_object_or_404(Category, cond)
        return Response(CategorySerializer(obj).data)


# КАТЕГОРИИ
# Описание логики по каждому ключу
FILTER_DEFS = {
    # FK-поля
    "manufacturer": {"kind": "fk", "field": "manufacturer"},
    "color": {"kind": "fk", "field": "color"},
    "type_material": {"kind": "fk", "field": "type_material"},
    "product_type": {"kind": "fk", "field": "product_type"},
    "frosen_defend": {"kind": "fk", "field": "frosen_defend"},
    "strength_grade": {"kind": "fk", "field": "strength_grade"},
    "water_resistance": {"kind": "fk", "field": "water_resistance"},

    # M2M-поля
    "format": {"kind": "m2m", "field": "formats"},
    "emptiness": {"kind": "m2m", "field": "emptiness"},

    # Опциональные поля (если они есть в модели Product)
    "size": {"kind": "m2m", "field": "sizes"},
    "package_weight_kg": {"kind": "int", "field": "package_weight_kg"},
}


def _get_category(key: str) -> Category:
    if key.isdigit():
        try:
            return Category.objects.get(id=int(key))
        except Category.DoesNotExist:
            pass
    for f in ("link_name", "name"):
        try:
            return Category.objects.get(**{f: key})
        except Category.DoesNotExist:
            continue
    raise Http404("Категория не найдена")


def _getlist(request, name: str):
    vals = request.GET.getlist(name)
    if len(vals) == 1 and "," in vals[0]:
        vals = [v for v in vals[0].split(",") if v]
    return vals


class CategoryFiltersAPIView(APIView):
    """
    GET /api/categories/<category_key>/filters/
    Возвращает только те фильтры, которые включены у категории.
    """

    def get(self, request, category_key: str):
        cat = _get_category(category_key)
        enabled = cat.filters_enabled or []
        qs = Product.objects.filter(category=cat)

        result = {"category": {"id": cat.id, "name": cat.name}, "filters": {}}

        for key in enabled:
            cfg = FILTER_DEFS.get(key)
            if not cfg:
                continue

            kind = cfg["kind"]
            field = cfg["field"]

            # пропускаем, если такого поля нет у модели (на случай опциональных)
            if not hasattr(Product, field):
                continue

            if kind == "fk":
                rows = (qs.values(f"{field}_id", f"{field}__name")
                        .exclude(**{f"{field}_id__isnull": True})
                        .annotate(count=Count("id"))
                        .order_by(f"{field}__name"))
                result["filters"][key] = [
                    {"id": r[f"{field}_id"], "name": r[f"{field}__name"], "count": r["count"]}
                    for r in rows
                ]

            elif kind == "m2m":
                rows = (qs.values(f"{field}__id", f"{field}__name")
                        .exclude(**{f"{field}__id__isnull": True})
                        .annotate(count=Count("id", distinct=True))
                        .order_by(f"{field}__name"))
                result["filters"][key] = [
                    {"id": r[f"{field}__id"], "name": r[f"{field}__name"], "count": r["count"]}
                    for r in rows
                ]

            elif kind == "int":
                rows = (qs.values(field)
                        .exclude(**{f"{field}__isnull": True})
                        .annotate(count=Count("id"))
                        .order_by(field))
                result["filters"][key] = [
                    {"value": r[field], "name": str(r[field]), "count": r["count"]}
                    for r in rows
                ]

        return Response(result)


class CategoryProductsAPIView(generics.ListAPIView):
    """
    GET /api/categories/<category_key>/products/?manufacturer=1,2&format=5&package_weight_kg=25
    Возвращает [{id, name, card_image}, ...] с учётом ТОЛЬКО включённых фильтров категории.
    """
    serializer_class = ProductInCatSerializer

    def get_queryset(self):
        cat = _get_category(self.kwargs["category_key"])
        enabled = set(cat.filters_enabled or [])
        qs = Product.objects.filter(category=cat).distinct()

        for key in enabled:
            cfg = FILTER_DEFS.get(key)
            if not cfg or not hasattr(Product, cfg["field"]):
                continue
            vals = _getlist(self.request, key)
            if not vals:
                continue

            kind = cfg["kind"]
            field = cfg["field"]

            if kind == "fk":
                qs = qs.filter(**{f"{field}_id__in": vals})
            elif kind == "m2m":
                ids = [int(v) for v in vals if str(v).isdigit()]
                if ids:
                    qs = (
                        qs.filter(**{f"{field}__id__in": ids})
                        .annotate(
                            _sel_cnt=Count(
                                field,
                                filter=Q(**{f"{field}__id__in": ids}),
                                distinct=True
                            )
                        )
                        .filter(_sel_cnt=len(ids))
                    )
            elif kind == "int":
                # числа: позволим и "25,30", и "?package_weight_kg=25&package_weight_kg=30"
                try:
                    ints = [int(v) for v in vals]
                    qs = qs.filter(**{f"{field}__in": ints})
                except ValueError:
                    pass

        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


# 3) Мини-инфо по списку id (для корзины)
class BasketItemsAPIView(APIView):
    """
    GET  /api/products/bulk-min/?ids=1,2,3
    POST /api/products/bulk-min/   body: {"ids":[1,2,3]}
    -> [{id, name, card_image}, ...]
    """

    def _load_ids(self, request):
        ids = _getlist(request, "ids")
        if not ids and isinstance(request.data, dict):
            ids = request.data.get("ids") or []
        try:
            return [int(i) for i in ids]
        except Exception:
            return []

    def get(self, request):
        ids = self._load_ids(request)
        if not ids:
            return Response({"detail": "Передайте ids"}, status=status.HTTP_400_BAD_REQUEST)
        qs = Product.objects.filter(id__in=ids)
        ser = ProductInCatSerializer(qs, many=True, context={"request": request})
        return Response(ser.data)

    def post(self, request):
        return self.get(request)


# 4) Детальная карточка товара
class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    GET /api/products/<int:pk>/
    Возвращает все характеристики и все фото товара.
    """
    serializer_class = ProductDetailSerializer
    queryset = (
        Product.objects
        .select_related("manufacturer", "type_material", "category", "color",
                        "frosen_defend", "strength_grade", "water_resistance", "product_type")
        .prefetch_related("formats", "emptiness", "images")
    )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


def product_client_view(request, pk: int):
    # Никаких данных о товаре тут не подгружаем — рендерим на клиенте
    return render(request, "product_detail.html", {"product_id": pk})


from django.views.generic import TemplateView


class CatalogView(TemplateView):
    template_name = "catalog.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        ctx["category_slug"] = slug or "all"
        return ctx


from django.db.models import Q, Count


class AllProductsAPIView(generics.ListAPIView):
    serializer_class = ProductInCatSerializer

    def get_queryset(self):
        qs = Product.objects.all().distinct()

        # применяем все поддерживаемые ключи из FILTER_DEFS, если они есть в запросе
        for key, cfg in FILTER_DEFS.items():
            field = cfg["field"]
            if not hasattr(Product, field):
                continue

            vals = _getlist(self.request, key)
            if not vals:
                continue

            kind = cfg["kind"]
            if kind == "fk":
                qs = qs.filter(**{f"{field}_id__in": vals})

            elif kind == "m2m":
                # ПЕРЕСЕЧЕНИЕ: товар должен содержать все выбранные значения
                ids = [int(v) for v in vals if str(v).isdigit()]
                if ids:
                    qs = (
                        qs.filter(**{f"{field}__id__in": ids})
                        .annotate(
                            _sel_cnt=Count(
                                field,
                                filter=Q(**{f"{field}__id__in": ids}),
                                distinct=True
                            )
                        )
                        .filter(_sel_cnt=len(ids))
                    )

            elif kind == "int":
                try:
                    ints = [int(v) for v in vals]
                    qs = qs.filter(**{f"{field}__in": ints})
                except ValueError:
                    pass

        # серверная сортировка (совместимо с фронтом)
        ordering = self.request.query_params.get("ordering")
        if ordering:
            qs = qs.order_by(ordering)
        else:
            qs = qs.order_by("-id")

        return qs


from collections import defaultdict
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product

# Поля, по которым строим фильтры (добавьте/уберите свои)
FILTER_FIELDS = ['manufacturer', 'color', 'type_material', 'product_type']


def _collect_filter_for_field(qs, field_name: str):
    """
    Собирает список опций для одного поля.
    - Если поле ForeignKey -> вернёт [{'id', 'name', 'count'}, ...]
    - Если поле обычное (CharField и т.п.) -> вернёт [{'value', 'count'}, ...]
    """
    model = qs.model
    field = model._meta.get_field(field_name)

    # ForeignKey / реляционное поле
    if field.is_relation and not field.many_to_many and not field.one_to_many:
        related_model = field.remote_field.model

        # Считаем количество товаров на каждую опцию (по id связанной модели)
        counts = (
            qs.values(field_name)
            .annotate(count=Count('id'))
            .order_by()
        )
        counts_map = {row[field_name]: row['count'] for row in counts if row[field_name] is not None}

        # Тянем имя опции из связанной модели (пытаемся взять name/title, иначе str)
        qs_related = related_model.objects.filter(id__in=list(counts_map.keys())) \
            .values('id', 'name')  # если у вас другое поле названия — ниже есть запасной вариант
        items = []
        have_name_field = 'name' in qs_related.query.values_select

        # Если в связанной модели поле называется не name, попробуем title
        if not have_name_field:
            qs_related = related_model.objects.filter(id__in=list(counts_map.keys())).values('id', 'title')
            have_title_field = 'title' in qs_related.query.values_select
            if have_title_field:
                for r in qs_related:
                    items.append({
                        'id': r['id'],
                        'name': r.get('title'),
                        'count': counts_map.get(r['id'], 0),
                    })
            else:
                # Фоллбек: берём объекты и приводим к str (дороже, но надёжно)
                for obj in related_model.objects.filter(id__in=list(counts_map.keys())):
                    items.append({
                        'id': obj.id,
                        'name': getattr(obj, 'name', getattr(obj, 'title', str(obj))),
                        'count': counts_map.get(obj.id, 0),
                    })
        else:
            for r in qs_related:
                items.append({
                    'id': r['id'],
                    'name': r.get('name'),
                    'count': counts_map.get(r['id'], 0),
                })

        # Сортируем по имени для стабильности
        items.sort(key=lambda x: (x['name'] or '').lower())
        return items

    # Нереляционное поле (CharField и т.п.)
    values_qs = (
        qs.exclude(**{f"{field_name}__isnull": True})
        .exclude(**{field_name: ""})
        .values(field_name)
        .annotate(count=Count('id'))
        .order_by(field_name)
    )
    return [
        {'value': row[field_name], 'count': row['count']}
        for row in values_qs
    ]


@api_view(['GET'])
def global_filters(request):
    """
    GET /api/filters/
    Возвращает доступные фильтры для всего каталога (когда категория не выбрана).
    Структура ответа:
    {
      "filters": {
        "manufacturer": [{"id","name","count"}...] или [{"value","count"}...],
        "color": [...],
        "material_type": [...],
        "product_type": [...]
      }
    }
    Параметры:
      ?only=manufacturer,color  — ограничить список полей
      ?published=true|false     — если в модели есть флаг публикации
    """
    qs = Product.objects.all()

    # (опционально) фильтр по опубликованным — если у вас есть такое поле
    published_param = request.query_params.get('published')
    if published_param in ('1', 'true', 'True'):
        if any(f.name == 'published' for f in Product._meta.get_fields()):
            qs = qs.filter(published=True)

    # Ограничение списка полей через ?only=
    only = request.query_params.get('only')
    fields = FILTER_FIELDS
    if only:
        requested = {f.strip() for f in only.split(',')}
        fields = [f for f in FILTER_FIELDS if f in requested]

    # Оставляем только те поля, которые реально есть в модели
    product_field_names = {f.name for f in Product._meta.get_fields()}
    fields = [f for f in fields if f in product_field_names]

    data = {}
    for field in fields:
        data[field] = _collect_filter_for_field(qs, field)

    return Response({'filters': data})
