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
    show_all = request.GET.get('show_all', '').lower() == 'true'

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

    all_img_instances = ImagenResiduo.objects.filter(user=request.user).order_by('-creado')
    logger.debug(f"Found {all_img_instances.count()} ImagenResiduo objects for user {request.user.username}")

    all_history_items = []
    for img_instance in all_img_instances:
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
                        r'(\w+)\s*\((\d+)\)',
                        r'(\w+)\s*:?\s*(\d+)',
                        r'(\w+)',              
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
            else:
                logger.warning(f"Empty or null resultado for ImagenResiduo: ID={img_instance.id}")
                if total_count > 0:
                    residues_with_count = [{'residue': 'Desconocido', 'count': total_count}]
                else:
                    residues_with_count = [{'residue': 'Desconocido', 'count': 0}]

            local_tz = pytz.timezone(settings.TIME_ZONE)
            local_time = img_instance.creado.astimezone(local_tz)

            history_item = {
                'timestamp': local_time.strftime('%d/%m/%Y, %H:%M'),
                'residues': residues_with_count,
                'weight': f"{total_count * 0.1:.1f}kg",
                'residue_types': [r['residue'].lower() for r in residues_with_count]
            }
            all_history_items.append(history_item)

        except Exception as e:
            logger.error(f"Error con imagen {img_instance.id}: {e}")
            continue

    if filter_residue and not show_all:
        filtered_items = []
        for item in all_history_items:
            if any(filter_residue in residue_type for residue_type in item['residue_types']):
                filtered_items.append(item)
        history_items = filtered_items
        logger.debug(f"Filtered by residue '{filter_residue}': {len(history_items)} items")
    else:
        history_items = all_history_items

    logger.debug(f"Final residue counts: {residue_counts}")
    logger.debug(f"Total items to paginate: {len(history_items)}")
    
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
        'filter_residue': filter_residue,
        'show_all': show_all
    })