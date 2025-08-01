from django.shortcuts import render
from shop_part.models import Product
from shop_part.serializers import ProductSerializer, ProductInCatSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from shop_part.models import Category, Product, TypeMaterial, Questions, Galery


# Create your views here.
class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


def index(request):
    return render(request, 'index.html')


def products(request):
    return render(request, 'category.html')

def galery(request):
    
    
    return render(request, 'galery.html')


def category(request):
    cat_id = Category.objects.get(link_name=request.GET.get('cat_name'))
    products = Product.objects.filter(category=cat_id)
    products = ProductInCatSerializer(products, many=True, context={'request': request})
    print(products.data[0])
    return render(request, 'category.html', {'products': products.data, 'cat_name': ["Главная",cat_id.name], 'questions' : Questions.objects.all()})


def about(request):
    return render(request, 'about.html')
