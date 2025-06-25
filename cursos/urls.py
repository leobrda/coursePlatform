from django.urls import path
from . import views

app_name = 'cursos'

urlpatterns = [
    path('registrar/', views.register, name='registrar'),
    path('registrar/concluido/', views.register_done, name='registrar_concluido'),
]