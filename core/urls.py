from django.contrib import admin
from django.urls import path, include
from cursos import views as cursos_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cursos/', include('cursos.urls', namespace='cursos')),

    path('', cursos_views.listar_cursos, name='home'),
]