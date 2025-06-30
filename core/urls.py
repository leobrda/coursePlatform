from django.contrib import admin
from django.urls import path, include
from cursos import views as cursos_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cursos/', include('cursos.urls', namespace='cursos')),

    path('', cursos_views.listar_cursos, name='home'),

    path('categoria/<slug:category_slug>/', cursos_views.listar_cursos, name='lista_cursos_por_categoria'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)