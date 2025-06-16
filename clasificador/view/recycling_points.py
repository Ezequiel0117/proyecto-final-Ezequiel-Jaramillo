from ..models import PuntoReciclaje
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from ..models import PuntoReciclaje
from django.http import JsonResponse
from ..models import CustomUser


@login_required
def mapa(request):
    puntos = PuntoReciclaje.objects.all()
    return render(request, 'mapa/mapa.html', {'puntos': puntos})

@csrf_exempt
def guardar_punto(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            provincia = data.get('provincia')
            ciudad = data.get('ciudad')
            
            punto = PuntoReciclaje.objects.create(
                nombre=data.get('nombre'),
                latitud=data.get('latitud'),
                longitud=data.get('longitud'),
                materiales=data.get('materiales'),
                capacidad_kg=int(data.get('capacidad_kg')),
                provincia=provincia,
                ciudad = ciudad
            )
            return JsonResponse({'status': 'ok', 'id': punto.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'mensaje': str(e)})

@csrf_exempt
def eliminar_punto(request, punto_id):
    if request.method == "DELETE":
        try:
            punto = PuntoReciclaje.objects.get(id=punto_id)
            punto.delete()
            return JsonResponse({"status": "ok"})
        except PuntoReciclaje.DoesNotExist:
            return JsonResponse({"status": "error", "mensaje": "Punto no encontrado"}, status=404)
    return JsonResponse({"status": "error", "mensaje": "Método no permitido"}, status=405)
