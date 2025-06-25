from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomLoginView, register, register_done

app_name = 'cursos'

urlpatterns = [
    path('registrar/', views.register, name='registrar'),
    path('registrar/concluido/', views.register_done, name='registrar_concluido'),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='cursos:login'), name='logout'),
]