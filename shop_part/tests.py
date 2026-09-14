import csv
from decimal import Decimal
from io import StringIO

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class ProductPriceTests(TestCase):
    def test_legacy_product_without_price_remains_valid(self):
        category = Category.objects.create(name="Кирпич")
        product = Product(name="Товар без цены", category=category)
        product.full_clean()
        product.save()

        response = self.client.get(reverse("api-product-detail", args=[product.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["price"])
        self.assertIsNone(response.json()["old_price"])
        self.assertEqual(response.json()["currency"], "RUB")

    def test_old_price_must_be_higher_than_current_price(self):
        product = Product(
            name="Некорректная скидка",
            price=Decimal("100.00"),
            old_price=Decimal("90.00"),
        )

        with self.assertRaises(ValidationError) as error:
            product.full_clean()

        self.assertIn("old_price", error.exception.message_dict)

    def test_old_price_requires_current_price(self):
        product = Product(name="Нет актуальной цены", old_price=Decimal("150.00"))

        with self.assertRaises(ValidationError) as error:
            product.full_clean()

        self.assertIn("old_price", error.exception.message_dict)


class YandexFeedTests(TestCase):
    expected_header = [
        "ID", "ID2", "URL", "Image", "Title", "Description",
        "Price", "Currency", "Old Price",
        "custom_label_0", "custom_label_1", "custom_label_2",
        "custom_label_3", "custom_label_4", "custom_score",
    ]

    def parse_feed(self):
        response = self.client.get(reverse("yandex_feed"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        return list(csv.reader(StringIO(response.content.decode("utf-8"))))

    def test_feed_contains_utf8_prices_and_escaped_text(self):
        product = Product.objects.create(
            name='Кирпич "Красный", гладкий',
            description="<p>Описание, товара</p>\nвторая строка",
            card_image="products/red-brick.jpg",
            price=Decimal("1250.50"),
            old_price=Decimal("1400.00"),
            currency="RUB",
            feed_id2="RED-01",
            custom_label_0="Акция",
            custom_score=7,
        )

        rows = self.parse_feed()

        self.assertEqual(rows[0], self.expected_header)
        self.assertEqual(len(rows), 2)
        row = dict(zip(rows[0], rows[1]))
        self.assertEqual(row["ID"], str(product.pk))
        self.assertEqual(row["ID2"], "RED-01")
        self.assertEqual(row["Title"], 'Кирпич "Красный", гладкий')
        self.assertEqual(row["Description"], "Описание, товара вторая строка")
        self.assertEqual(row["Price"], "1250.50")
        self.assertEqual(row["Currency"], "RUB")
        self.assertEqual(row["Old Price"], "1400.00")
        self.assertEqual(row["custom_score"], "7")
        self.assertTrue(row["URL"].endswith(f"/p/{product.pk}/"))
        self.assertTrue(row["Image"].endswith("/uploads/products/red-brick.jpg"))

    def test_feed_keeps_price_columns_empty_for_legacy_product(self):
        Product.objects.create(name="Старый товар без цены")

        rows = self.parse_feed()
        row = dict(zip(rows[0], rows[1]))

        self.assertEqual(row["Price"], "")
        self.assertEqual(row["Currency"], "")
        self.assertEqual(row["Old Price"], "")

    def test_disabled_product_is_not_exported(self):
        Product.objects.create(name="Не выгружать", feed_enabled=False)

        rows = self.parse_feed()

        self.assertEqual(rows, [self.expected_header])


class ProductDetailPageTests(TestCase):
    def test_price_block_and_calculation_button_replace_old_callback_block(self):
        product = Product.objects.create(name="Товар")

        response = self.client.get(reverse("product_client_view", args=[product.pk]))
        html = response.content.decode("utf-8")

        self.assertContains(response, "Запросить расчет")
        self.assertContains(response, 'id="price"')
        self.assertNotIn("Узнать цену", html)
        self.assertNotIn("Заказать обратный звонок", html)
        self.assertNotIn("Заказать звонок", html)
