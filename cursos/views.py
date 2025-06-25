from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import logout


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
