from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import logout
from .models import Curso


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('registrar_concluido')
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
