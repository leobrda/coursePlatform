from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomLoginView, register, register_done, detalhe_curso, ver_aula, editar_perfil, logout_view, adicionar_resposta, votar_resposta, marcar_aula_concluida

app_name = 'cursos'

urlpatterns = [
    path('registrar/', register, name='registrar'),
    path('registrar/concluido/', register_done, name='registrar_concluido'),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),

    path('curso/<int:pk>/', detalhe_curso, name='detalhe_curso'),
    path('aula/<int:pk>/', ver_aula, name='ver_aula'),
    path('pergunta/<int:pk_pergunta>/responder/', adicionar_resposta, name='adicionar_resposta'),
    path('resposta/<int:pk_resposta>/votar/', votar_resposta, name='votar_resposta'),
    path('aula/<int:pk_aula>/concluir/', marcar_aula_concluida, name='marcar_aula_concluida'),

    path('minha-conta/', editar_perfil, name='editar_perfil'),
]