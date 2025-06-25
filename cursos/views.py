from django.shortcuts import render, redirect
from .forms import UserRegistrationForm


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