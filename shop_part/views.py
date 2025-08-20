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

def galery(request):
    # та самая коллекция карточек — сортируем по position и сразу подтягиваем связанные SmallGallery
    items = BigGalery.objects.all().order_by('position').prefetch_related('images')
    return render(request, 'galery.html', {
        'items': items,
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
    return render(request, 'category.html', {'products': products.data, 'cat_name': ["Главная",cat_id.name], 'questions' : Questions.objects.all()})


def about(request):
    return render(request, 'about.html')

class FAQView(ListView):
    model = Questions
    template_name = "accordion.html"   # см. файл ниже
    context_object_name = "questions"
    queryset = Questions.objects.all().order_by("id")
@require_POST
def contact_request_create(request):
    # простая валидация
    data = request.POST
    # Маппинг: принимаем и "старые" и ваши имена полей
    first_name  = (data.get("first_name") or data.get("name") or "").strip()
    last_name   = (data.get("last_name") or data.get("surname") or "").strip()
    email       = (data.get("email") or "").strip()
    phone       = (data.get("phone") or "").strip()
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