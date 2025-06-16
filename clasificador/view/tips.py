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

    consejos = []
    for residuo in ['plastico', 'papel', 'vidrio', 'metal']:
        count = residuos_por_clase[residuo]
        if count == 0:
            consejos.append("Sigue reciclando para lograr darte un consejo")
        elif count <= 5:
            consejos.append("Sigue reciclando para lograr darte un consejo")
        else:
            if residuo == 'plastico':
                if count >= 10:
                    consejos.append("¡Has reciclado muchas botellas plásticas! Prueba usar botellas reutilizables para reducir tus desechos semanales.")
                elif count > 5:
                    consejos.append("Estás reciclando plásticos, ¡gran inicio! Considera llevar tus propias bolsas de tela al supermercado.")
            elif residuo == 'papel':
                if count >= 10:
                    consejos.append("¡Buen trabajo con el papel! ¿Sabías que el papel puede reciclarse varias veces? Reduce su uso cuando sea posible.")
                elif count > 5:
                    consejos.append("Has reciclado bastante papel. Intenta reducir su uso en casa.")
            elif residuo == 'vidrio':
                if count > 10:
                    consejos.append("¡Genial! ¿Sabías que el vidrio puede reciclarse indefinidamente? Evita botellas plásticas y opta por envases de vidrio cuando puedas.")
                elif count > 5:
                    consejos.append("Estás reciclando vidrio, ¡excelente! Usa envases de vidrio reutilizables para más impacto.")
            elif residuo == 'metal':
                if count >= 10:
                    consejos.append("¡Impresionante cantidad de metal reciclado! Lleva bolsas de tela al supermercado y reutilízalas.")
                elif count > 5:
                    consejos.append("Buen progreso con el metal. Intenta separar más metales para maximizar tu impacto ambiental.")

    return render(request, 'consejos/consejos.html', {
        'consejos': consejos,
        'residuos_por_clase': residuos_por_clase
    })