from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.
# User Model
class UserModel(AbstractUser):
    USER_TYPE_CHOICES = (
        ('buyer', 'Comprador'),
        ('seller', 'Vendedor'),
    )
    fullname = models.CharField(max_length=100, verbose_name='Nombres Completos')
    fullLastName = models.CharField(max_length=100, verbose_name='Apellidos Completos')
    idNumber = models.CharField(max_length=20, verbose_name='Número de Cédula')
    phoneNumber = models.CharField(max_length=12, verbose_name='Número de Teléfono')
    userType = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, verbose_name='Tipo de Usuario', default='buyer')
    

#Products Model

class ProductModel(models.Model):
    PRODUCTS_NAME_CHOICES = [
        ('aguacate', 'Aguacate'),
        ('banana', 'Banano'),
        ('brocoli', 'Brócoli'),
        ('cafe', 'Café'),
        ('cebolla_cabezona', 'Cebolla Cabezona'),
        ('cebolla_larga', 'Cebolla Larga'),
        ('coliflor', 'Coliflor'),
        ('frijol', 'Frijol'),
        ('guayaba', 'Guayaba'),
        ('lechuga', 'Lechuga'),
        ('limon', 'Limón'),
        ('lulo', 'Lulo'),
        ('maiz', 'Maíz'),
        ('mango', 'Mango'),
        ('maracuya', 'Maracuyá'),
        ('naranja', 'Naranja'),
        ('papa', 'Papa'),
        ('papaya', 'Papaya'),
        ('platano', 'Platano'),
        ('piña', 'Piña'),
        ('sandia', 'Sandía'),
        ('tomate', 'Tomate'),
        ('yuca', 'Yuca'),
        ('zanahoria', 'Zanahoria')
    ]
    UNITS_CHOICES = (
        ('kg', 'Kilogramos'),
        ('lb', 'Libras'),
        ('unit', 'Unidades'),
    )
    
    
    productName = models.CharField(max_length=30,choices=PRODUCTS_NAME_CHOICES, verbose_name='Nombre del Producto')
    specificName = models.CharField(max_length=100, verbose_name='Nombre Específico')
    maxQuantity = models.IntegerField(verbose_name='Cantidad Máxima')
    minQuantity = models.IntegerField(verbose_name='Cantidad Mínima')
    unit = models.CharField(max_length=10, choices=UNITS_CHOICES, verbose_name='Unidad de Medida')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,verbose_name='Vendedor')
    sellerId = models.CharField(max_length=10,verbose_name='Cedula del Vendedor')
    categories = models.CharField(max_length=100, verbose_name='Categorías')
    pricePeerUnit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio por Unidad',default=1000)

    
    def __str__(self):
        return f"{self.productName} - {self.specificName}"
    


# Cart Model
class cartModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario')
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, verbose_name='Producto')
    quantity = models.PositiveIntegerField(verbose_name='Cantidad')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de adición')

    def __str__(self):
        return f"{self.user.username} - {self.product.productName} (x{self.quantity})"

    def totalPrice(self):
        return self.quantity * self.product.pricePeerUnit


# Order Model
class OrderModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Total')
    idPaid = models.BooleanField(default=False, verbose_name='¿Pagado?')
    
    def __str__(self):
        return f'pedido #{self.id} - {self.user.username} - {self.created_at}'

class OrderItemModel(models.Model):
    order = models.ForeignKey(OrderModel,related_name='items', on_delete=models.CASCADE, verbose_name='Pedido')
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, verbose_name='Producto')
    quantity = models.PositiveIntegerField(verbose_name='Cantidad')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    
    def __str__(self):
        return f"{self.product.productName} (x{self.quantity})"
    


   