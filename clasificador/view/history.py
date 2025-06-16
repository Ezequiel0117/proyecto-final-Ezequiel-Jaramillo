from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from ..models import ImagenResiduo
import os
import logging
import pytz
import re

logger = logging.getLogger(__name__)

@login_required
def history(request):
    media_path = os.path.join(settings.MEDIA_ROOT, 'residuos')
    history_items = []
    filter_residue = request.GET.get('residue', '').lower()

    # Consistentes y sin tildes
    residue_counts = {'plastico': 0, 'vidrio': 0, 'papel': 0, 'metal': 0}

    traducciones = {
        'plastic': 'plastico',
        'plástico': 'plastico',
        'plastico': 'plastico',
        'paper': 'papel',
        'papel': 'papel',
        'glass': 'vidrio',
        'vidrio': 'vidrio',
        'metal': 'metal'
    }

    img_instances = ImagenResiduo.objects.filter(user=request.user).order_by('-creado')
    logger.debug(f"Found {img_instances.count()} ImagenResiduo objects for user {request.user.username}")

    for img_instance in img_instances:
        try:
            filename = os.path.basename(img_instance.imagen.name)
            file_path = os.path.join(media_path, filename)
            if not os.path.exists(file_path):
                logger.warning(f"Image file not found: {file_path}")
                continue

            logger.debug(f"Processing ImagenResiduo: ID={img_instance.id}, Resultado='{img_instance.resultado}'")
            residues_with_count = []
            total_count = img_instance.cantidad_residuos or 0

            if img_instance.resultado and img_instance.resultado.strip():
                result_parts = [part.strip() for part in img_instance.resultado.split(',')]
                for part in result_parts:
                    logger.debug(f"Parsing result part: '{part}'")
                    patterns = [
                        r'(\w+)\s*\((\d+)\)',  # "plastico (2)"
                        r'(\w+)\s*:?\s*(\d+)', # "plastico: 2" or "plastico 2"
                        r'(\w+)',              # "plastico"
                    ]
                    match = None
                    for pattern in patterns:
                        match = re.match(pattern, part, re.IGNORECASE)
                        if match:
                            break
                    if match:
                        residue = match.group(1).lower()
                        count = int(match.group(2)) if len(match.groups()) > 1 else 1
                        normalized = traducciones.get(residue, residue)
                        residues_with_count.append({'residue': normalized.capitalize(), 'count': count})
                        if normalized in residue_counts:
                            residue_counts[normalized] += count
                            logger.debug(f"Updated count for {normalized}: {residue_counts[normalized]}")
                        else:
                            logger.warning(f"Unexpected residue type: {normalized} (original: {residue})")
                    else:
                        logger.warning(f"Failed to parse result part: '{part}'")
                        continue
                unique_residues = [r['residue'] for r in residues_with_count]
            else:
                logger.warning(f"Empty or null resultado for ImagenResiduo: ID={img_instance.id}")
                if total_count > 0:
                    residues_with_count = [{'residue': 'Desconocido', 'count': total_count}]
                    unique_residues = ['Desconocido']
                else:
                    residues_with_count = [{'residue': 'Desconocido', 'count': 0}]
                    unique_residues = ['Desconocido']

            if filter_residue and not any(res['residue'].lower() == filter_residue for res in residues_with_count):
                continue

            local_tz = pytz.timezone(settings.TIME_ZONE)
            local_time = img_instance.creado.astimezone(local_tz)

            history_items.append({
                'timestamp': local_time.strftime('%d/%m/%Y, %H:%M'),
                'residues': residues_with_count,
                'weight': f"{total_count * 0.1:.1f}kg"
            })

        except Exception as e:
            logger.error(f"Error con imagen {img_instance.id}: {e}")
            continue

    logger.debug(f"Final residue counts: {residue_counts}")
    paginator = Paginator(history_items, 16)
    page = request.GET.get('page')
    try:
        history_items_page = paginator.page(page)
    except PageNotAnInteger:
        history_items_page = paginator.page(1)
    except EmptyPage:
        history_items_page = paginator.page(paginator.num_pages)

    return render(request, 'historial/history.html', {
        'history_items': history_items_page,
        'residue_counts': residue_counts,
        'filter_residue': filter_residue
    })