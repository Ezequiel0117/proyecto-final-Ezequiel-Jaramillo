from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import FileInput
from .models import CustomUser
from .models import ImagenResiduo
from django.core.exceptions import ValidationError
import os
from PIL import Image
import io

class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(max_length=20, label="Teléfono")
    remember_me = forms.BooleanField(required=False, label="Recordarme")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password1', 'password2', 'remember_me']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya está registrado.')
        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            has_uppercase = any(c.isupper() for c in password)
            has_lowercase = any(c.islower() for c in password)
            has_number = any(c.isdigit() for c in password)
            has_special = any(c in '!@#$%^&*' for c in password)
            has_length = len(password) >= 8

            met_requirements = sum([has_uppercase, has_lowercase, has_number, has_special, has_length])

            if met_requirements < 3:
                raise ValidationError(
                    'La contraseña debe cumplir al menos tres de los siguientes requisitos: '
                    'una mayúscula, una minúscula, un número, un carácter especial (!@#$%^&*), y al menos 8 caracteres.'
                )
        return password

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages.update({
            'password_mismatch': 'Las contraseñas no coinciden.',
            'password_too_similar': 'La contraseña es demasiado similar a tu información personal.',
            'password_too_short': 'La contraseña debe tener al menos 8 caracteres.',
            'password_too_common': 'La contraseña es demasiado común.',
            'password_entirely_numeric': 'La contraseña no puede ser completamente numérica.',
        })

class CustomUserEditForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False
        self.fields['profile_picture'].widget = forms.FileInput(
            attrs={'class': 'form-control d-none', 'id': 'profilePictureInput'}
        )
        if self.instance.profile_picture:
            self.fields['profile_picture'].widget.attrs['data-current-picture'] = self.instance.profile_picture.url

class ImagenForm(forms.ModelForm):
    class Meta:
        model = ImagenResiduo
        fields = ['imagen']

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen:
            if imagen.size > 5 * 1024 * 1024:
                raise ValidationError('La imagen no debe exceder los 5MB.')

            valid_extensions = ['.jpg', '.jpeg', '.png']
            extension = os.path.splitext(imagen.name)[1].lower()
            if extension not in valid_extensions:
                raise ValidationError('Solo se permiten imágenes en formato JPEG o PNG.')

            try:
                img = Image.open(io.BytesIO(imagen.read()))
                img.verify() 
                imagen.seek(0)
            except Exception:
                raise ValidationError('El archivo subido no es una imagen válida.')

        return imagen