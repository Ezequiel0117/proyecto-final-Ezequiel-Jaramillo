import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import ImagenResiduo
import logging
from datetime import timedelta
import matplotlib.pyplot as plt
import io


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@login_required
def api_metricas(request):
    try:
        user = request.user
        thirty_days_ago = timezone.now() - timedelta(days=30)
        residuos = ImagenResiduo.objects.filter(user=user, creado__gte=thirty_days_ago)

        plasticos = 0
        papel = 0
        vidrio = 0
        metal = 0
        peso_por_residuo = 0.1
        arboles_por_kg = 1

        for residuo in residuos:
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

        total_residuos = sum(residuo.cantidad_residuos for residuo in residuos)
        total_kg = plasticos + papel + vidrio + metal
        co2_por_kg = 2.0
        degradacion_por_kg = 100
        mejora_ambiental = min(100, (total_residuos / 60) * 100)

        arboles = (papel * arboles_por_kg * 2) + ((plasticos + vidrio + metal) * arboles_por_kg)

        data = {
            "resumen": {
                "residuos_clasificados": total_residuos,
                "plasticos": round(plasticos, 1),
                "papel": round(papel, 1),
                "vidrio": round(vidrio, 1),
                "metal": round(metal, 1)
            },
            "impacto": {
                "co2_ev": round(total_kg * co2_por_kg, 1),
                "arboles": round(arboles, 1),
                "degradacion": round(total_kg * degradacion_por_kg, 1),
                "mejora": round(mejora_ambiental, 1)
            },
            "progreso": {
                "actual": total_residuos
            }
        }
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error al obtener métricas: {str(e)}")
        return JsonResponse({
            "error": f"Error al obtener métricas: {str(e)}",
            "resumen": {"residuos_clasificados": 0, "plasticos": 0, "papel": 0, "vidrio": 0, "metal": 0},
            "impacto": {"co2_ev": 0, "arboles": 0, "degradacion": 0, "mejora": 0},
            "progreso": {"actual": 0}
        }, status=500)

@login_required
def export_metrics_pdf(request):
    try:
        user = request.user
        thirty_days_ago = timezone.now() - timedelta(days=30)
        residuos = ImagenResiduo.objects.filter(user=user, creado__gte=thirty_days_ago)

        plasticos, papel, vidrio, metal = 0, 0, 0, 0
        peso_por_residuo = 0.1
        arboles_por_kg = 1

        for residuo in residuos:
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

        total_residuos = sum(residuo.cantidad_residuos for residuo in residuos)
        total_kg = plasticos + papel + vidrio + metal
        co2_evitado = total_kg * 2.0
        arboles_salvados = (papel * arboles_por_kg * 2) + ((plasticos + vidrio + metal) * arboles_por_kg)

        fig = plt.figure(figsize=(8.5, 11), facecolor='white')
        gs = fig.add_gridspec(4, 2, hspace=0.5, wspace=0.3, 
                             left=0.1, right=0.9, top=0.9, bottom=0.1)
        
        ax_header = fig.add_subplot(gs[0, :])
        ax_header.axis('off')
        
        fecha_actual = timezone.now().strftime('%d/%m/%Y')
        header_text = f"""REPORTE DE RECICLAJE
        
Usuario: {user.username}
Período: Últimos 30 días
Fecha: {fecha_actual}"""
        
        ax_header.text(0.5, 0.5, header_text, ha='center', va='center',
                      fontsize=16, fontweight='bold', color='#2c3e50',
                      transform=ax_header.transAxes)
        
        ax_header.axhline(y=0.1, xmin=0.1, xmax=0.9, color='#34495e', linewidth=2)
        
        ax_summary = fig.add_subplot(gs[1, :])
        ax_summary.axis('off')
        
        summary_data = [
            ['MÉTRICA', 'VALOR'],
            ['Total de residuos clasificados', f'{total_residuos} unidades'],
            ['Peso total reciclado', f'{total_kg:.1f} kg'],
            ['CO₂ evitado', f'{co2_evitado:.1f} kg'],
            ['Árboles salvados', f'{arboles_salvados:.0f}'],
        ]
        
        table_summary = ax_summary.table(cellText=summary_data[1:], colLabels=summary_data[0],
                                       cellLoc='left', loc='center',
                                       bbox=[0.1, 0.2, 0.8, 0.6])
        table_summary.auto_set_font_size(False)
        table_summary.set_fontsize(12)
        table_summary.scale(1, 2.5)
        
        for i in range(len(summary_data[0])):
            table_summary[(0, i)].set_facecolor('#34495e')
            table_summary[(0, i)].set_text_props(weight='bold', color='white')
            
        for i in range(1, len(summary_data)):
            for j in range(len(summary_data[0])):
                table_summary[(i, j)].set_facecolor('#ecf0f1' if i % 2 == 0 else 'white')
                if j == 1:
                    table_summary[(i, j)].set_text_props(weight='bold', color='#2c3e50')
        
        ax_bars = fig.add_subplot(gs[2, 0])
        categories = ['Plásticos', 'Papel', 'Vidrio', 'Metal']
        values = [plasticos, papel, vidrio, metal]
        colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
        
        bars = ax_bars.bar(categories, values, color=colors, alpha=0.8, 
                          edgecolor='white', linewidth=1)
        ax_bars.set_ylabel('Kilogramos', fontweight='bold', color='#2c3e50')
        ax_bars.set_title('Composición por Categoría', fontweight='bold', 
                         color='#2c3e50', pad=20)
        ax_bars.grid(axis='y', alpha=0.3, linestyle='--')
        ax_bars.set_facecolor('#fafafa')
        
        for bar, value in zip(bars, values):
            if value > 0:
                ax_bars.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                           f'{value:.1f}', ha='center', va='bottom', 
                           fontweight='bold', color='#2c3e50')
        
        ax_bars.tick_params(axis='x', rotation=0, colors='#2c3e50')
        ax_bars.tick_params(axis='y', colors='#2c3e50')
        
        ax_pie = fig.add_subplot(gs[2, 1])
        
        if total_kg > 0:
            sizes = [plasticos, papel, vidrio, metal]
            labels = ['Plásticos', 'Papel', 'Vidrio', 'Metal']
            colors_pie = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
            
            filtered_data = [(size, label, color) for size, label, color 
                           in zip(sizes, labels, colors_pie) if size > 0]
            
            if filtered_data:
                sizes_filtered, labels_filtered, colors_filtered = zip(*filtered_data)
                
                wedges, texts, autotexts = ax_pie.pie(sizes_filtered, labels=labels_filtered,
                                                    colors=colors_filtered, autopct='%1.1f%%',
                                                    startangle=90, textprops={'fontsize': 10})
                
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    
            ax_pie.set_title('Distribución Porcentual', fontweight='bold', 
                           color='#2c3e50', pad=20)
        else:
            ax_pie.text(0.5, 0.5, 'Sin datos disponibles', ha='center', va='center',
                       fontsize=14, color='#7f8c8d', transform=ax_pie.transAxes)
            ax_pie.set_title('Distribución Porcentual', fontweight='bold', 
                           color='#2c3e50', pad=20)
        
        ax_detail = fig.add_subplot(gs[3, :])
        ax_detail.axis('off')
        
        detail_data = [
            ['CATEGORÍA', 'PESO (kg)', 'PORCENTAJE'],
            ['Plásticos', f'{plasticos:.1f}', f'{(plasticos/total_kg*100) if total_kg > 0 else 0:.1f}%'],
            ['Papel', f'{papel:.1f}', f'{(papel/total_kg*100) if total_kg > 0 else 0:.1f}%'],
            ['Vidrio', f'{vidrio:.1f}', f'{(vidrio/total_kg*100) if total_kg > 0 else 0:.1f}%'],
            ['Metal', f'{metal:.1f}', f'{(metal/total_kg*100) if total_kg > 0 else 0:.1f}%'],
            ['', '', ''],
            ['TOTAL', f'{total_kg:.1f}', '100.0%']
        ]
        
        table_detail = ax_detail.table(cellText=detail_data[1:], colLabels=detail_data[0],
                                     cellLoc='center', loc='center',
                                     bbox=[0.2, 0.1, 0.6, 0.8])
        table_detail.auto_set_font_size(False)
        table_detail.set_fontsize(11)
        table_detail.scale(1, 2)
        
        for i in range(len(detail_data[0])):
            table_detail[(0, i)].set_facecolor('#2c3e50')
            table_detail[(0, i)].set_text_props(weight='bold', color='white')
        
        for i in range(1, len(detail_data)):
            for j in range(len(detail_data[0])):
                if i == len(detail_data) - 1:
                    table_detail[(i, j)].set_facecolor('#34495e')
                    table_detail[(i, j)].set_text_props(weight='bold', color='white')
                elif i == len(detail_data) - 2:
                    table_detail[(i, j)].set_facecolor('white')
                else:
                    table_detail[(i, j)].set_facecolor('#f8f9fa' if i % 2 == 0 else 'white')
        
        # Guardar PDF
        buffer = io.BytesIO()
        plt.savefig(buffer, format='pdf', bbox_inches='tight', dpi=300,
                   facecolor='white', edgecolor='none')
        plt.close()
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f"reporte_reciclaje_{user.username}_{timezone.now().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error al generar el PDF de métricas: {str(e)}")
        return JsonResponse({
            'error': 'Error interno del servidor al generar el reporte',
            'message': 'Por favor, inténtalo de nuevo más tarde.'
        }, status=500)