from django.urls import path, reverse_lazy
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
    painel_instrutor,
    aprovar_associado,
    gerir_curso_form,
    gerir_aulas,
    aula_form,
    apagar_aula,
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

    path('meu-painel-instrutor/', painel_instrutor, name='painel_instrutor'),
    path('associado/<int:pk_associado>/aprovar/', aprovar_associado, name='aprovar_associado'),
    path('meu-painel-instrutor/cursos/novo/', gerir_curso_form, name='criar_curso'),
    path('meu-painel-instrutor/cursos/<int:pk>/editar/', gerir_curso_form, name='editar_curso'),
    path('meu-painel-instrutor/cursos/<int:pk_curso>/aulas/', gerir_aulas, name='gerir_aulas'),
    path('meu-painel-instrutor/cursos/<int:pk_curso>/aulas/nova/', aula_form, name='adicionar_aula'),
    path('meu-painel-instrutor/aulas/<int:pk_aula>/editar/', aula_form, name='editar_aula'),
    path('meu-painel-instrutor/aulas/<int:pk_aula>/apagar/', apagar_aula, name='apagar_aula'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='cursos/password_reset_form.html', success_url=reverse_lazy('cursos:password_reset_done'), email_template_name='registration/password_reset_email.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='cursos/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='cursos/password_reset_confirm.html', success_url=reverse_lazy('cursos:password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='cursos/password_reset_complete.html'), name='password_reset_complete'),
]