from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserEditForm, PerguntaForm, RespostaForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import logout
from .models import Curso, Aula, Pergunta, Resposta, Associado, Categoria


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
def listar_cursos(request, category_slug=None):
    categoria_selecionada = None
    cursos = Curso.objects.all()
    categorias = Categoria.objects.all()

    if category_slug:
        categoria_selecionada = get_object_or_404(Categoria, slug=category_slug)
        cursos = cursos.filter(categorias=categoria_selecionada)

    context = {
        'cursos': cursos,
        'categorias': categorias,
        'categoria_selecionada': categoria_selecionada,
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
def ver_aula(request, pk):
    aula = get_object_or_404(Aula, pk=pk)

    if request.method == 'POST':
        if 'submit_pergunta' in request.POST:
            form_pergunta = PerguntaForm(request.POST)
            if form_pergunta.is_valid():
                nova_pergunta = form_pergunta.save(commit=False)
                nova_pergunta.aula = aula
                nova_pergunta.usuario = request.user
                nova_pergunta.save()
                return redirect('cursos:ver_aula', pk=aula.pk)
        elif 'submit_reposta' in request.POST:
            form_resposta = RespostaForm(request.POST)
            pergunta_id = request.POST.get('pergunta_id')
            if form_resposta.is_valid() and pergunta_id:
                pergunta = get_object_or_404(Pergunta, pk=pergunta_id)
                nova_resposta = form_resposta.save(commit=False)
                nova_resposta.pergunta = pergunta
                nova_resposta.usuario = request.user
                nova_resposta.save()
                return redirect('cursos:ver_aula', pk=aula.pk)

    form_pergunta = PerguntaForm()
    form_resposta = RespostaForm()
    perguntas_da_aula = Pergunta.objects.filter(aula=aula).prefetch_related('respostas__usuario', 'respostas__votos')

    embed_url = f"https://www.youtube.com/embed/{aula.youtube_video_id}"

    context = {
        'aula': aula,
        'embed_url': embed_url,
        'perguntas': perguntas_da_aula,
        'form_pergunta': form_pergunta,
        'form_resposta': form_resposta,
    }

    return render(request, 'cursos/ver_aula.html', context=context)


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



@login_required
def votar_resposta(request, pk_resposta):
    resposta = get_object_or_404(Resposta, pk=pk_resposta)

    if resposta.votos.filter(id=request.user.id).exists():
        resposta.votos.remove(request.user)
    else:
        resposta.votos.add(request.user)

    return redirect('cursos:ver_aula', pk=resposta.pergunta.aula.pk)


@login_required
def marcar_aula_concluida(request, pk_aula):
    aula = get_object_or_404(Aula, pk=pk_aula)

    associado = get_object_or_404(Associado, usuario=request.user)

    if aula in associado.aulas_concluidas.all():
        associado.aulas_concluidas.remove(aula)
    else:
        associado.aulas_concluidas.add(aula)

    return redirect('cursos:detalhe_curso', pk=aula.curso.pk)