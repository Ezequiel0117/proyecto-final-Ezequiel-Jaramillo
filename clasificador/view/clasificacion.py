import cv2
import numpy as np
import base64
import os
from ultralytics import YOLO
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from ..models import ImagenResiduo
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

modelo = None

def initialize_model():
    global modelo
    if modelo is None:
        modelo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Modelos', 'best.pt')
        logger.debug(f"Intentando cargar modelo desde: {modelo_path}")
        if not os.path.exists(modelo_path):
            logger.error(f"Modelo no encontrado en: {modelo_path}")
            raise FileNotFoundError(f"Modelo 'best.pt' no encontrado en {modelo_path}")
        modelo = YOLO(modelo_path)
        try:
            dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
            modelo.predict(source=dummy_img, save=False)
            logger.debug("Modelo YOLO cargado exitosamente.")
        except Exception as e:
            logger.error(f"Error al calentar el modelo: {e}")
            raise
    return modelo

initialize_model()

CONFIDENCE_THRESHOLD = 0.5
MAX_BOX_AREA_RATIO = 0.3

@login_required
def clasificar_residuo(request):
    logger.debug("Clasificando imagen subida")
    residuos_con_confianza = []
    imagen_url = None
    error = None

    if request.method == 'POST' and 'imagen' in request.FILES:
        imagen_file = request.FILES['imagen']
        instancia = ImagenResiduo(user=request.user, imagen=imagen_file)
        try:
            instancia.save()
            imagen_path = instancia.imagen.path
            img = cv2.imread(imagen_path)
            if img is None:
                raise ValueError("No se pudo leer la imagen.")

            results = modelo.predict(source=img, save=False)
            clases_detectadas = results[0].names
            indices = results[0].boxes.cls.tolist()
            boxes = results[0].boxes.xyxy.tolist()
            confs = results[0].boxes.conf.tolist()

            traducciones = {
                'plastic': 'plastico',
                'paper': 'papel',
                'glass': 'vidrio',
                'metal': 'metal'
            }

            residuos_por_clase = {}
            for i, box, conf in zip(indices, boxes, confs):
                if conf < CONFIDENCE_THRESHOLD:
                    continue

                clase = clases_detectadas[int(i)]
                residuo = traducciones.get(clase.lower(), clase.lower())
                if residuo not in residuos_por_clase:
                    residuos_por_clase[residuo] = {'confidencias': [], 'boxes': [], 'count': 0}
                residuos_por_clase[residuo]['confidencias'].append(conf)
                residuos_por_clase[residuo]['boxes'].append(box)
                residuos_por_clase[residuo]['count'] += 1

            total_residuos = sum(d['count'] for d in residuos_por_clase.values())
            resultados = ', '.join([f"{r} ({d['count']})" for r, d in residuos_por_clase.items()])
            instancia.resultado = resultados
            instancia.cantidad_residuos = total_residuos
            instancia.save()

            for residuo, datos in residuos_por_clase.items():
                max_conf = max(datos['confidencias'])
                for box in datos['boxes']:
                    x_min, y_min, x_max, y_max = map(int, box)
                    cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    cv2.putText(img, f"{residuo} ({round(max_conf * 100, 1)}%)",
                                (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            output_dir = os.path.join(settings.MEDIA_ROOT, 'residuos', 'processed')
            os.makedirs(output_dir, exist_ok=True)
            output_filename = f"processed_{os.path.basename(imagen_path)}"
            output_path = os.path.join(output_dir, output_filename)
            if not cv2.imwrite(output_path, img):
                raise ValueError("No se pudo guardar la imagen procesada.")
            imagen_url = f"{settings.MEDIA_URL}residuos/processed/{output_filename}"

            for residuo, datos in residuos_por_clase.items():
                max_conf = max(datos['confidencias'])
                residuos_con_confianza.append({
                    'clase': residuo,
                    'confianza': round(max_conf * 100, 1),
                    'cantidad': datos['count']
                })

        except Exception as e:
            instancia.delete()
            error = f"Error al procesar imagen: {str(e)}"
            logger.error(error)

    return render(request, 'clasificar_residuo/subir.html', {
        'form': None,
        'residuos_con_confianza': residuos_con_confianza,
        'imagen_url': imagen_url,
        'error': error
    })

@login_required
def procesar_frame(request):
    logger.debug("Procesando frame de cámara")
    if request.method == 'POST':
        data = request.POST.get('frame')
        if not data:
            return JsonResponse({'error': 'No se recibió frame'}, status=400)

        try:
            img_data = base64.b64decode(data.split(',')[1])
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            return JsonResponse({'error': 'Error al decodificar imagen'}, status=400)

        results = modelo.predict(source=img, save=False)
        clases_detectadas = results[0].names
        indices = results[0].boxes.cls.tolist()
        boxes = results[0].boxes.xyxy.tolist()
        confidences = results[0].boxes.conf.tolist()

        traducciones = {
            'plastic': 'plastico',
            'paper': 'papel',
            'glass': 'vidrio',
            'metal': 'metal'
        }

        h, w, _ = img.shape
        detecciones = []

        for i, box, conf in zip(indices, boxes, confidences):
            if conf < CONFIDENCE_THRESHOLD:
                continue

            x_min, y_min, x_max, y_max = box
            box_area = (x_max - x_min) * (y_max - y_min)
            if box_area / (w * h) > MAX_BOX_AREA_RATIO:
                continue

            clase = clases_detectadas[int(i)]
            residuo = traducciones.get(clase.lower(), clase.lower())
            detecciones.append({
                'clase': residuo,
                'box': [int(x_min), int(y_min), int(x_max), int(y_max)],
                'confidence': round(float(conf), 2)
            })

        if not detecciones:
            return JsonResponse({'detecciones': []})

        return JsonResponse({'detecciones': detecciones})

    return JsonResponse({'error': 'Método no permitido'}, status=405)
