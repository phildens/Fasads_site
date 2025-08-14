from django.shortcuts import render
from shop_part.models import Product
from shop_part.serializers import ProductSerializer, ProductInCatSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from shop_part.models import Category, Product, TypeMaterial, Questions
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import ContactRequest

# Create your views here.
class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


def index(request):
    return render(request, 'index.html')


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

@require_POST
def contact_request_create(request):
    # простая валидация
    first_name  = (request.POST.get("first_name") or "").strip()
    last_name   = (request.POST.get("last_name") or "").strip()
    email       = (request.POST.get("email") or "").strip()
    phone       = (request.POST.get("phone") or "").strip()
    description = (request.POST.get("description") or "").strip()

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