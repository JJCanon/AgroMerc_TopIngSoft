from django.http import JsonResponse
from django.views import View
from .models import ProductModel

class ProductListAPIView(View):
    def get(self, request):
        products = ProductModel.objects.all()
        data = []

        for product in products:
            data.append({
                'id': product.id,
                'productName': product.productName,
                'specificName': product.specificName,
                'maxQuantity': product.maxQuantity,
                'minQuantity': product.minQuantity,
                'unit': product.unit,
                'categories': product.categories,
                'pricePerUnit': float(product.pricePeerUnit),
                'seller': {
                    'username': product.seller.username,
                    'fullName': product.seller.fullname,
                    'fullLastName': product.seller.fullLastName,
                    'idNumber': product.sellerId,
                }
            })

        return JsonResponse({'products': data}, safe=False)
