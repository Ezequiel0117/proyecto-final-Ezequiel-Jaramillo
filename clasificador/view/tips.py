from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import ImagenResiduo

@login_required
def consejos(request):
    residuos = ImagenResiduo.objects.filter(user=request.user).order_by('-creado')

    residuos_por_clase = {'plastico': 0, 'papel': 0, 'vidrio': 0, 'metal': 0}

    for residuo in residuos:
        if residuo.resultado and residuo.cantidad_residuos > 0:
            clases = residuo.resultado.lower().split(', ')
            for clase in clases:
                if 'plastico' in clase:
                    residuos_por_clase['plastico'] += int(clase.split('(')[1].split(')')[0])
                elif 'papel' in clase:
                    residuos_por_clase['papel'] += int(clase.split('(')[1].split(')')[0])
                elif 'vidrio' in clase:
                    residuos_por_clase['vidrio'] += int(clase.split('(')[1].split(')')[0])
                elif 'metal' in clase:
                    residuos_por_clase['metal'] += int(clase.split('(')[1].split(')')[0])

    consejos = {}
    for tipo in residuos_por_clase:
        cantidad = residuos_por_clase[tipo]
        if cantidad == 0:
            consejos[tipo] = "Sigue reciclando para lograr darte un consejo."
        elif cantidad <= 5:
            consejos[tipo] = "¡Buen comienzo! Sigue reciclando más " + tipo + " para recibir un mejor consejo."
        else:
            if tipo == 'plastico':
                consejos[tipo] = "¡Has reciclado muchas botellas plásticas! Prueba usar botellas reutilizables para reducir tus desechos."
            elif tipo == 'papel':
                consejos[tipo] = "¡Buen trabajo con el papel! Recuerda reutilizar hojas por ambos lados y reciclar periódicos."
            elif tipo == 'vidrio':
                consejos[tipo] = "¡Excelente! El vidrio puede reciclarse indefinidamente. Usa frascos de vidrio cuando sea posible."
            elif tipo == 'metal':
                consejos[tipo] = "¡Impresionante reciclaje de metal! Considera reutilizar latas como organizadores en casa."

    return render(request, 'consejos/consejos.html', {
        'residuos_por_clase': residuos_por_clase,
        'consejos': consejos
    })
