from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import ProductModel, cartModel, OrderModel, OrderItemModel
from .forms import UserSignUpForm, ProductForm
from django.urls import reverse
from django.test import Client


# Create your tests here.
User = get_user_model()

## Models Tests
# Test for UserModel
class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email="test@example.com",
            password='testPassword01.',
            fullname='Test User',
            fullLastName='Test Lastname',
            idNumber='123456789',
            phoneNumber='3109874565',
            userType='buyer'
        )
        self.assertEqual(user.fullname, 'Test User')
        self.assertEqual(user.userType, "buyer")
        self.assertTrue(user.check_password('testPassword01.'))


# Test for ProductModel
class ProductModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="seller2",
            userType="seller",
            idNumber="3182267897"
        )
    
    def test_create_product(self):
        product = ProductModel.objects.create(
            productName="aguacate",
            specificName="Aguacate Hass",
            maxQuantity=100,
            minQuantity=5,
            unit="kg",
            seller=self.user,
            sellerId=self.user.idNumber,
            categories="Frutas tropicales",
            pricePeerUnit=5000
        )
        self.assertEqual(str(product), "aguacate - Aguacate Hass")
        self.assertEqual(product.categories, "Frutas tropicales")
        
# Test for CartModel
class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.product = ProductModel.objects.create(
            productName="banana",
            specificName="Banano común",
            maxQuantity=100,
            minQuantity=10,
            unit="kg",
            seller=self.user,
            sellerId=self.user.idNumber,
            pricePeerUnit=2000,
        )
    def test_add_to_cart(self):
        cart_item = cartModel.objects.create(
            user=self.user,
            product=self.product,
            quantity=10
        ) 
        self.assertEqual(cart_item.totalPrice(), 20000)


## Formularies Tests

# test for UserSignUpForm
class UserSignUpFormTest(TestCase):
    def test_valid_signup_form(self):
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
            "fullname": "Test User",
            "fullLastName": "Test Lastname",
            "idNumber": "123456789",
            "phoneNumber": "3109874565",
            "userType": "buyer"
        }
        form = UserSignUpForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_invalid_signup_form(self):
        form_data={
            "username": "testuser",
            "password1": "testPassword01.",
            "password2": "testPassword02.", # Passwords don't match
        }
        form = UserSignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        
# test for ProductForm
class ProductFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            userType="seller"
        )
        
    def test_valid_product_form(self):
        form_data = {
            "productName": "aguacate",
            "specificName": "Aguacate Hass",
            "maxQuantity": 100,
            "minQuantity": 5,
            "unit": "kg",
            "pricePeerUnit": 5000,
            "seller": self.user.id,
            "sellerId": self.user.idNumber
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_invalid_product_form(self):
        form_data = {
            "productName": "aguacate",
            "maxQuantity": -10  # Negative Quantity (invalid)
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        
## Views Tests
# Test for AddToCartView
class AddToCartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testPassword01.",
            userType="buyer"
        )
        self.product = ProductModel.objects.create(
            productName="banana",
            specificName="Banano común",
            maxQuantity=100,
            minQuantity=10,
            unit="kg",
            seller=self.user,
            sellerId=self.user.idNumber,
            pricePeerUnit=2000,
        )
    def test_add_to_cart(self):
        self.client.login(username="testuser", password="testPassword01.")
        response = self.client.post(
            reverse("addToCart",args=[self.product.id]),
            {"quantity": 10}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(cartModel.objects.count(), 1)

# Test for CheckoutView
class CheckoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testPassword01.",
            userType="buyer"
        )
        self.product = ProductModel.objects.create(
            productName="banana",
            specificName="Banano común",
            maxQuantity=100,
            minQuantity=10,
            unit="kg",
            seller=self.user,
            sellerId=self.user.idNumber,
            pricePeerUnit=2000,
        )
        self.cart_item = cartModel.objects.create(
            user=self.user,
            product=self.product,
            quantity=10
        )
    
    def test_checkout(self):
        self.client.login(username="testuser", password="testPassword01.")
        response = self.client.post(reverse("checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(OrderModel.objects.count(), 1)
        self.assertEqual(OrderItemModel.objects.count(), 1)
