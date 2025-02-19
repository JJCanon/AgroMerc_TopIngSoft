from django import forms
from .models import UserModel

# Sign Up
from django import forms
from .models import UserModel

class UserForm(forms.ModelForm):
    
    userType = forms.ChoiceField(
        choices=[('buyer', 'Comprador'), ('seller', 'Vendedor')],
        label="Tipo de usuario",
        initial='buyer',  # Opción por defecto
    )
    
    class Meta:  # ¡Aquí debe ser "Meta" con mayúscula!
        model = UserModel
        fields = [
            'fullName',
            'fullLastName',
            'idNumber',
            'email',
            'phoneNumber',
            'userName',
            'password',
            'userType'
        ]
        labels = {
            'fullName': 'Nombres Completos',
            'fullLastName': 'Apellidos Completos',
            'idNumber': 'Número de Cédula',
            'email': 'Correo Electrónico',
            'phoneNumber': 'Número de Celular',
            'userName': 'Nombre de Usuario',
            'password': 'Contraseña',
            'userType': 'Tipo de Usuario',
        }
        widgets = {
            'password': forms.PasswordInput(),  # Visualización de contraseña
        }
        
# Sign In
class SignInForm(forms.Form):
    userName = forms.CharField( max_length=255, label="Nombre de Usuario")
    password = forms.CharField( max_length=255, label="Contraseña", widget=forms.PasswordInput())