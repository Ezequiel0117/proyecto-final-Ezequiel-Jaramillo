from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.db.models import IntegerField as modelsIntegerField
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static
from django.db import IntegrityError
from django.db import models
from django.contrib.auth.forms import AuthenticationForm
from ..models import ImagenResiduo, CustomUser
from ..forms import CustomUserCreationForm, CustomUserEditForm
from django.utils import timezone
from django.db.models import Sum, Case, When
from datetime import datetime


def home(request):
    if request.user.is_authenticated and 'profile_pic_url' not in request.session:
        if request.user.profile_picture:
            request.session['profile_pic_url'] = request.user.profile_picture.url
        else:
            request.session['profile_pic_url'] = '/static/img/user.webp'
    return render(request, 'core/home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'auth/signup.html', {
            'form': CustomUserCreationForm()
        })
    else:
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)
                return redirect('home')
            except IntegrityError:
                return render(request, 'auth/signup.html', {
                    'form': form,
                    'error': 'Este nombre de usuario ya está en uso.'
                })
        else:
            return render(request, 'auth/signup.html', {
                'form': form,
                'error': 'Por favor, revisa los datos ingresados.'
            })

def signin(request):
    if request.method == 'GET':
        return render(request, 'auth/signin.html', {
            'form': AuthenticationForm()
        })
    else:
        form = AuthenticationForm(data=request.POST)
        print("Datos recibidos:", request.POST) 
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'auth/signin.html', {
                    'form': form,
                    'error': 'Nombre de usuario y contraseña no coinciden.'
                })
        else:
            return render(request, 'auth/signin.html', {
                'form': form,
                'error': 'Por favor revisa los datos ingresados.'
            })

@login_required
def signout(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            if request.user.profile_picture:
                request.session['profile_pic_url'] = request.user.profile_picture.url
            else:
                request.session['profile_pic_url'] = static('img/user.webp')
            return redirect('profile')
    else:
        form = CustomUserEditForm(instance=request.user)

    if not request.session.get('profile_pic_url'):
        if request.user.profile_picture:
            request.session['profile_pic_url'] = request.user.profile_picture.url
        else:
            request.session['profile_pic_url'] = static('img/user.webp')

    now = timezone.now()
    inicio_mes = timezone.make_aware(datetime(now.year, now.month, 1))

    residuos_mes = ImagenResiduo.objects.filter(user=request.user, creado__gte=inicio_mes)
    total_residuos_mes = sum(residuo.cantidad_residuos for residuo in residuos_mes)

    residuos_total = ImagenResiduo.objects.filter(user=request.user)
    total_residuos_global = sum(residuo.cantidad_residuos for residuo in residuos_total)

    plasticos = 0
    papel = 0
    vidrio = 0
    metal = 0
    peso_por_residuo = 0.1

    for residuo in residuos_mes:
        if residuo.resultado and residuo.cantidad_residuos > 0:
            clases = residuo.resultado.lower().split(', ')
            for clase in clases:
                if 'plastico' in clase:
                    plasticos += residuo.cantidad_residuos * peso_por_residuo
                elif 'papel' in clase:
                    papel += residuo.cantidad_residuos * peso_por_residuo
                elif 'vidrio' in clase:
                    vidrio += residuo.cantidad_residuos * peso_por_residuo
                elif 'metal' in clase:
                    metal += residuo.cantidad_residuos * peso_por_residuo

    ranking = (CustomUser.objects.filter(is_superuser=False)
               .annotate(
                   total_residuos_mes=Sum(
                       Case(
                           When(imagen_residuo_set__creado__gte=inicio_mes,
                                then='imagen_residuo_set__cantidad_residuos'),
                           default=0,
                           output_field=modelsIntegerField()
                       )
                   ),
                   total_residuos_global=Sum(
                       'imagen_residuo_set__cantidad_residuos',
                       output_field=modelsIntegerField()
                   )
               )
               .values('username', 'first_name', 'last_name', 'total_residuos_mes', 'total_residuos_global')
               .order_by('-total_residuos_mes')[:10])

    ranking_list = list(ranking)
    ranking_position = None
    for i, user in enumerate(ranking_list, 1):
        if user['username'] == request.user.username:
            ranking_position = i
            break

    logros = [
        {'nombre': 'Eco Warrior', 'descripcion': 'Recicla 10 residuos', 'residuos_requeridos': 10, 'completado': total_residuos_global >= 10},
        {'nombre': 'Green Champion', 'descripcion': 'Recicla 50 residuos', 'residuos_requeridos': 50, 'completado': total_residuos_global >= 50},
        {'nombre': 'Planet Saver', 'descripcion': 'Recicla 100 residuos', 'residuos_requeridos': 100, 'completado': total_residuos_global >= 100},
    ]

    context = {
        'form': form,
        'user_stats': {
            'total_residuos_mes': total_residuos_mes,
            'total_residuos_global': total_residuos_global,
            'ranking_position': ranking_position or '-',
        },
        'resumen': {
            'residuos_clasificados': total_residuos_mes,
            'plasticos': round(plasticos, 1),
            'papel': round(papel, 1),
            'vidrio': round(vidrio, 1),
            'metal': round(metal, 1),
        },
        'ranking': ranking_list,
        'logros': logros,
    }

    return render(request, 'core/profile.html', context)