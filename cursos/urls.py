from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    CustomLoginView,
    register, register_done,
    detalhe_curso,
    ver_aula,
    meu_painel,
    logout_view,
    votar_resposta,
    marcar_aula_concluida,
    lista_notificacoes,
)

app_name = 'cursos'

urlpatterns = [
    path('registrar/', register, name='registrar'),
    path('registrar/concluido/', register_done, name='registrar_concluido'),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),

    path('curso/<int:pk>/', detalhe_curso, name='detalhe_curso'),
    path('aula/<int:pk>/', ver_aula, name='ver_aula'),
    path('resposta/<int:pk_resposta>/votar/', votar_resposta, name='votar_resposta'),
    path('aula/<int:pk_aula>/concluir/', marcar_aula_concluida, name='marcar_aula_concluida'),

    path('minha-conta/', meu_painel, name='meu_painel'),

    path('notificacoes/', lista_notificacoes, name='notificacoes'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='cursos/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='cursos/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='cursos/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='cursos/password_reset_complete.html'), name='password_reset_complete'),
]