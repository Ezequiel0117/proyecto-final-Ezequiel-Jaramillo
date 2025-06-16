from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import requests
import re
import os

@login_required
def environmental_news(request):
    api_key = os.environ.get("API_KEY_NEWSAPI", ""),
    search_query = request.GET.get('q', '').strip()
    days = request.GET.get('days', '7')
    try:
        days = int(days)
        if days not in [7, 14, 30]:
            days = 7
    except ValueError:
        days = 7

    from_date = (timezone.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    if search_query:
        search_query = re.sub(r'[^\w\s-]', '', search_query)
        search_query = search_query[:30]

    base_query = ('"climate change" OR sustainability OR recycling OR pollution OR '
                  '"renewable energy" OR "waste management" OR "zero waste" OR '
                  'biodiversity OR conservation OR "carbon footprint"')
    query = f"({base_query}) {search_query}" if search_query else base_query

    if len(query) > 500:
        return render(request, 'noticias/environmental_news.html', {
            'articles': [],
            'message': 'La búsqueda es demasiado larga. Usa términos más cortos.',
            'search_query': search_query,
            'days': days
        })

    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': query,
        'from': from_date,
        'sortBy': 'relevancy',
        'apiKey': api_key,
    }

    articles = []
    message = ''

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        new_articles = data.get('articles', [])[:10]
        keywords = ['clima', 'ambiente', 'reciclaje', 'sostenibilidad', 'contaminación', 'energía']
        filtered_articles = [
            article for article in new_articles
            if any(keyword in ((article.get('title', '') or '') + (article.get('description', '') or '')).lower()
                   for keyword in keywords)
        ] or new_articles
        articles = filtered_articles
        message = f"Noticias actualizadas para: {search_query or 'temas ambientales'} en los últimos {days} días."
    except requests.exceptions.HTTPError as e:
        message = f"Error HTTP al obtener noticias: {e.response.status_code} - {e.response.text}"
    except requests.exceptions.RequestException as e:
        message = f"Error al conectar con la API: {e}"
    except ValueError as e:
        message = f"Error al procesar la respuesta de la API: {e}"

    return render(request, 'noticias/environmental_news.html', {
        'articles': articles,
        'message': message,
        'search_query': search_query,
        'days': days
    })