from rest_framework import serializers
from .models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "link_name", "card_image", "filters_enabled")
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductInCatSerializer(serializers.ModelSerializer):
    card_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'card_image']

    def get_card_image(self, obj):
        request = self.context.get('request')
        if obj.card_image and request:
            # obj.card_image.url → '/media/…'
            return request.build_absolute_uri(obj.card_image.url)
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    card_image = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    # Вложенные «{id, name}» для FK
    manufacturer = serializers.SerializerMethodField()
    type_material = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    frosen_defend = serializers.SerializerMethodField()
    strength_grade = serializers.SerializerMethodField()
    water_resistance = serializers.SerializerMethodField()
    product_type = serializers.SerializerMethodField()

    # M2M списком «{id, name}»
    formats = serializers.SerializerMethodField()
    emptiness = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id", "name", "description", "card_image", "images",
            "manufacturer", "type_material", "category", "color",
            "frosen_defend", "strength_grade", "water_resistance",
            "product_type", "formats", "emptiness",
        )

    def _abs(self, request, file_field):
        return request.build_absolute_uri(file_field.url) if (file_field and request) else None

    def _fk(self, obj, attr, field_name):
        ref = getattr(obj, attr, None)
        return {"id": ref.id, "name": ref.name, "field_name": field_name} if ref else None

    def get_card_image(self, obj):
        request = self.context.get("request")
        return self._abs(request, obj.card_image)

    def get_images(self, obj):
        request = self.context.get("request")
        urls = []
        for gi in obj.images.all():  # related_name='images' в Gallery :contentReference[oaicite:2]{index=2}
            if gi.image:
                urls.append(self._abs(request, gi.image))
        return urls

    def get_manufacturer(self, obj):
        return self._fk(obj, "manufacturer", "Производитель")

    def get_type_material(self, obj):
        return self._fk(obj, "type_material", "Тип материала")

    def get_category(self, obj):
        return self._fk(obj, "category", "Категория")

    def get_color(self, obj):
        return self._fk(obj, "color", "Цвет")

    def get_frosen_defend(self, obj):
        return self._fk(obj, "frosen_defend", "Морозостойкость")

    def get_strength_grade(self, obj):
        return self._fk(obj, "strength_grade", "Марка прочности")

    def get_water_resistance(self, obj):
        return self._fk(obj, "water_resistance", "Влагостойкость")

    def get_product_type(self, obj):
        return self._fk(obj, "product_type", "Тип продукта")

    def get_formats(self, obj):
        return [{"id": f.id, "name": f.name} for f in obj.formats.all()]

    def get_emptiness(self, obj):
        return [{"id": e.id, "name": e.name} for e in obj.emptiness.all()]
