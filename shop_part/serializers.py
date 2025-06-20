from rest_framework import serializers
from .models import Product


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
