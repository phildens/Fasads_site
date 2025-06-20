from django.shortcuts import render
from shop_part.models import Product
from shop_part.serializers import ProductSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
# Create your views here.
class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


def index(request):
    return render(request, 'index.html')


def products(request):
    return render(request, 'category.html')