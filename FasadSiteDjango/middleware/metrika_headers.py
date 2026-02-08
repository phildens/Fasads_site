# class DisableCoopForMetrikaMiddleware:
#     """
#     Убираем COOP только когда сайт открыт из интерфейса Яндекс.Метрики
#     (мастер выбора элемента для целей).
#     """
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         response = self.get_response(request)
#
#         referer = request.META.get("HTTP_REFERER", "")
#         if "metrika.yandex.ru" in referer:
#             # Удаляем COOP, даже если его добавил SecurityMiddleware или прокси
#             for header in (
#                 "Cross-Origin-Opener-Policy",
#                 "Cross-Origin-Opener-Policy-Report-Only",
#             ):
#                 if header in response:
#                     del response[header]
#
#         return response
