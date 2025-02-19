from django.db import models


# Create your models here.


class UserModel(models.Model):
    USER_TYPE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    )
    fullName = models.CharField(max_length=255, verbose_name="Nombres completos")
    fullLastName = models.CharField(max_length=255, verbose_name="Apellidos completos")
    idNumber = models.CharField(max_length=20, verbose_name="Número de Cédula")
    email = models.EmailField(max_length=255, verbose_name="Correo electrónico")
    phoneNumber = models.CharField(max_length=15, verbose_name="Número de celular")
    userName = models.CharField(max_length=255, verbose_name="Nombre de usuario")
    password = models.CharField(max_length=255, verbose_name="Contraseña")
    userType = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, verbose_name="Tipo de Usuario", default='buyer')
    
    def __str__(self):
        return f"{self.fullName} {self.fullLastName} ({self.userType})"
    