# shop_part/urls.py
from django.urls import path
from .views import (
    CategoryFiltersAPIView, CategoryProductsAPIView,
    BasketItemsAPIView, ProductDetailAPIView, AllProductsAPIView, CategoryDetailAPIView, SimilarProductsAPIView
)
from .views import CatalogView

urlpatterns = [
    path("api/categories/<str:category_key>/", CategoryDetailAPIView.as_view(), name="api-category-detail"),  # ← НОВОЕ

    path("api/categories/<str:category_key>/filters/", CategoryFiltersAPIView.as_view(), name="api-category-filters"),
    path("api/categories/<str:category_key>/products/", CategoryProductsAPIView.as_view(),
         name="api-category-products"),
    path("api/products/bulk-min/", BasketItemsAPIView.as_view(), name="api-basket-min"),
    path("api/products/<int:pk>/", ProductDetailAPIView.as_view(), name="api-product-detail"),
    path("catalog/", CatalogView.as_view(), name="catalog_all"),
    path("catalog/<slug:slug>/", CatalogView.as_view(), name="catalog_category"),
    path("api/catalog/", AllProductsAPIView.as_view(), name="api-all-products"),
    path("api/products/<int:pk>/similar/", SimilarProductsAPIView.as_view(), name="api_product_similar"),

]
