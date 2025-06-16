from django.contrib import admin
from django.urls import path
from clasificador.view.authentication import signin, signup, signout, profile, home
from clasificador.view.history import history
from clasificador.view.clasificacion import clasificar_residuo, procesar_frame
from clasificador.view.metrics import api_metricas, export_metrics_pdf
from clasificador.view.news import environmental_news
from clasificador.view.recycling_points import mapa, guardar_punto , eliminar_punto
from clasificador.view.tips import consejos
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home , name='home'),
    path('signup/', signup, name='signup'),
    path('signin/', signin, name='signin'),
    path('logout/', signout, name='logout'),
    path('profile/', profile, name='profile'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('noticias/', environmental_news, name='noticias'),
    path('api/metricas/', api_metricas, name='api_metricas'),
    path('clasificar/', clasificar_residuo, name='clasificar'),
    path('history/', history, name='history'),
    path('procesar-frame/', procesar_frame, name='procesar_frame'),
    path('export-metrics-pdf/', export_metrics_pdf, name='export_metrics_pdf'),
    path('mapa/', mapa, name='mapa'),
    path('guardar-punto/', guardar_punto, name='guardar_punto'),
    path('eliminar-punto/<int:punto_id>/', eliminar_punto, name='eliminar_punto'),
    path('consejos/', consejos, name='consejos'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)