from django.shortcuts import render
from shop_part.models import Product, Category, TypeMaterial, Questions, Manufactor, Color, ProductType
from shop_part.serializers import ProductInCatSerializer
from rest_framework.generics import ListAPIView
from shop_part.serializers import ProductSerializer


class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def products(request):
    return render(request, 'category.html')


def category(request):
    cat_link = request.GET.get('cat_name')
    cat = Category.objects.get(link_name=cat_link)
    products_qs = Product.objects.filter(category=cat)

    # Фильтры
    filter_manufacturer = request.GET.getlist('manufacturer')
    filter_color = request.GET.getlist('color')
    filter_material = request.GET.getlist('material')
    filter_type = request.GET.getlist('type')

    if filter_manufacturer:
        products_qs = products_qs.filter(manufacturer__id__in=filter_manufacturer)
    if filter_color:
        products_qs = products_qs.filter(color__id__in=filter_color)
    if filter_material:
        products_qs = products_qs.filter(type_material__id__in=filter_material)
    if filter_type:
        products_qs = products_qs.filter(product_type__id__in=filter_type)

    products = ProductInCatSerializer(products_qs, many=True, context={'request': request})

    return render(request, 'category.html', {
        'products': products.data,
        'cat_name': ["Главная", cat.name],
        'questions': Questions.objects.all(),
        'filter_manufacturer': filter_manufacturer,
        'filter_color': filter_color,
        'filter_material': filter_material,
        'filter_type': filter_type,
        'manufacturers': Manufactor.objects.all(),
        'colors': Color.objects.all(),
        'materials': TypeMaterial.objects.all(),
        'product_types': ProductType.objects.all(),
    })
