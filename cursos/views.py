from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserEditForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import logout
from .models import Curso, Aula


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('cursos:registrar_concluido')
    else:
        form = UserRegistrationForm()

    return render(request, 'cursos/registrar.html', {'form': form})


def register_done(request):
    return render(request, 'cursos/registrar_concluido.html')


class CustomLoginView(LoginView):
    template_name = 'cursos/login.html'

    def form_valid(self, form):
        user = form.get_user()

        if hasattr(user, 'associado') and user.associado.aprovado:
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Sua conta ainda não foi aprovada por um administrador.')
            return self.form_invalid(form)


@login_required
def listar_cursos(request):
    cursos = Curso.objects.all()

    context = {
        'cursos': cursos,
    }

    return render(request, 'cursos/lista_cursos.html', context=context)


@login_required
def detalhe_curso(request, pk):
    curso = get_object_or_404(Curso, pk=pk)

    context = {
        'curso': curso,
    }

    return render(request, 'cursos/detalhe_curso.html', context=context)


@login_required
@login_required
def ver_aula(request, pk):
    aula = get_object_or_404(Aula, pk=pk)

    embed_url = f"https://www.youtube.com/embed/{aula.youtube_video_id}"

    contexto = {
        'aula': aula,
        'embed_url': embed_url,
    }

    return render(request, 'cursos/ver_aula.html', contexto)


@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = UserEditForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('cursos:editar_perfil')
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'cursos/editar_perfil.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('cursos:login')
