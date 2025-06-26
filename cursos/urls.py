from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomLoginView, register, register_done, detalhe_curso, ver_aula, editar_perfil

app_name = 'cursos'

urlpatterns = [
    path('registrar/', register, name='registrar'),
    path('registrar/concluido/', register_done, name='registrar_concluido'),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='cursos:login'), name='logout'),

    path('curso/<int:pk>/', detalhe_curso, name='detalhe_curso'),
    path('aula/<int:pk>/', ver_aula, name='ver_aula'),

    path('minha-conta/', editar_perfil, name='editar_perfil'),
]