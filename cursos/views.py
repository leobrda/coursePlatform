from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserEditForm, PerguntaForm, RespostaForm, CursoForm, AulaForm, CategoriaForm, TopicoDiscussaoForm, ComentarioTopicoForm, PerguntaQuizForm, OpcaoRespostaForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import logout
from django.http import Http404, HttpResponseForbidden
from .models import Curso, Aula, Pergunta, Resposta, Associado, Categoria, Notificacao, Organizacao, TopicoDiscussao, ComentarioTopico, Quiz, PerguntaQuiz, OpcaoResposta


def get_user_organization(request):
    try:
        return request.user.associado.organizacao
    except (Associado.DoesNotExist, AttributeError):
        return None

def register(request):
    organizacao_padrao = Organizacao.objects.first()
    if not organizacao_padrao:
        # Lidar com o caso de nenhuma organização existir (ex: mostrar uma página de erro)
        return render(request, 'cursos/erro_setup.html')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, organizacao=organizacao_padrao)
        if form.is_valid():
            form.save()
            return redirect('cursos:registrar_concluido')
    else:
        form = UserRegistrationForm(organizacao=organizacao_padrao)

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
    organizacao_usuario = get_user_organization(request)
    if not organizacao_usuario:
        return render(request, 'cursos/erro_permissao.html')

    cursos = Curso.objects.filter(organizacao=organizacao_usuario)
    categorias = Categoria.objects.filter(organizacao=organizacao_usuario)

    categoria_selecionada = None
    if category_slug:
        categoria_selecionada = get_object_or_404(Categoria, slug=category_slug, organizacao=organizacao_usuario)
        cursos = cursos.filter(categorias=categoria_selecionada)

    context = {
        'cursos': cursos,
        'categorias': categorias,
        'categoria_selecionada': categoria_selecionada,
    }

    return render(request, 'cursos/lista_cursos.html', context=context)


@login_required
def detalhe_curso(request, pk):
    organizacao_usuario = get_user_organization(request)
    if not organizacao_usuario:
        return render(request, 'cursos/erro_permissao.html')

    curso = get_object_or_404(Curso, pk=pk, organizacao=organizacao_usuario)

    context = {
        'curso': curso,
    }

    return render(request, 'cursos/detalhe_curso.html', context=context)


@login_required
def ver_aula(request, pk):
    organizacao_usuario = get_user_organization(request)
    if not organizacao_usuario:
        return render(request, 'cursos/erro_permissao.html')

    aula = get_object_or_404(Aula, pk=pk, curso__organizacao=organizacao_usuario)

    form_pergunta = PerguntaForm()
    form_resposta = RespostaForm()

    if request.method == 'POST':
        if 'submit_pergunta' in request.POST:
            form_pergunta = PerguntaForm(request.POST)
            if form_pergunta.is_valid():
                nova_pergunta = form_pergunta.save(commit=False)
                nova_pergunta.aula = aula
                nova_pergunta.usuario = request.user
                nova_pergunta.save()
                return redirect('cursos:ver_aula', pk=aula.pk)

        elif 'submit_resposta' in request.POST:
            form_resposta = RespostaForm(request.POST)
            pergunta_id = request.POST.get('pergunta_id')
            if form_resposta.is_valid() and pergunta_id:
                pergunta = get_object_or_404(Pergunta, pk=pergunta_id)
                nova_resposta = form_resposta.save(commit=False)
                nova_resposta.pergunta = pergunta
                nova_resposta.usuario = request.user
                nova_resposta.save()
                return redirect('cursos:ver_aula', pk=aula.pk)

    perguntas_da_aula = Pergunta.objects.filter(aula=aula)

    context = {
        'aula': aula,
        'perguntas': perguntas_da_aula,
        'form_pergunta': form_pergunta,
        'form_resposta': form_resposta,
        'embed_url': f'https://www.youtube.com/embed/{aula.youtube_video_id}',
    }

    return render(request, 'cursos/ver_aula.html', context=context)


@login_required
def meu_painel(request):
    organizacao_usuario = get_user_organization(request)
    associado = get_object_or_404(Associado, usuario=request.user
                                  )
    if not organizacao_usuario:
        return render(request, 'cursos/erro_permissao.html')

    if request.method == 'POST':
        form = UserEditForm(instance=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('cursos:meu_painel')
    else:
        form = UserEditForm(instance=request.user)

    minhas_perguntas = Pergunta.objects.filter(usuario=request.user)
    minhas_respostas = Resposta.objects.filter(usuario=request.user)
    meus_cursos_inscritos = associado.cursos_inscritos.all()

    context = {
        'form': form,
        'minhas_perguntas': minhas_perguntas,
        'minhas_respostas': minhas_respostas,
        'meus_cursos': meus_cursos_inscritos,
    }

    return render(request, 'cursos/meu_painel.html', context=context)


def logout_view(request):
    logout(request)
    return redirect('cursos:login')



@login_required
def votar_resposta(request, pk_resposta):
    organizacao_usuario = get_user_organization(request)
    if not organizacao_usuario:
        return render(request, 'cursos/erro_permissao.html')

    resposta = get_object_or_404(Resposta, pk=pk_resposta, pergunta__aula__curso__organizacao=organizacao_usuario)

    if resposta.votos.filter(id=request.user.id).exists():
        resposta.votos.remove(request.user)
    else:
        resposta.votos.add(request.user)

    return redirect('cursos:ver_aula', pk=resposta.pergunta.aula.pk)


@login_required
def marcar_aula_concluida(request, pk_aula):
    organizacao_usuario = get_user_organization(request)
    if not organizacao_usuario:
        return render(request, 'cursos/erro_permissao.html')

    aula = get_object_or_404(Aula, pk=pk_aula, curso__organizacao=organizacao_usuario)
    associado = request.user.associado

    if aula in associado.aulas_concluidas.all():
        associado.aulas_concluidas.remove(aula)
    else:
        associado.aulas_concluidas.add(aula)

    return redirect('cursos:detalhe_curso', pk=aula.curso.pk)


@login_required
def lista_notificacoes(request):
    notificacoes = Notificacao.objects.filter(destinatario=request.user)
    notificacoes.filter(lida=False).update(lida=True)

    context = {
        'notificacoes': notificacoes,
    }

    return render(request, 'cursos/notificacoes.html', context=context)


@login_required
def painel_instrutor(request):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except Organizacao.DoesNotExist:
        raise Http404

    total_associados = Associado.objects.filter(organizacao=organizacao).count()
    total_cursos = Curso.objects.filter(organizacao=organizacao).count()

    associados_pendentes = Associado.objects.filter(organizacao=organizacao, aprovado=False)
    cursos_da_organizacao = Curso.objects.filter(organizacao=organizacao)

    context = {
        'organizacao': organizacao,
        'total_associados': total_associados,
        'total_cursos': total_cursos,
        'associados_pendentes': associados_pendentes,
        'cursos': cursos_da_organizacao,
    }

    return render(request, 'cursos/painel_instrutor.html', context=context)


@login_required
def aprovar_associado(request, pk_associado):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except Organizacao.DoesNotExist:
        return HttpResponseForbidden("Você não tem permissão para realizar esta ação.")

    associado = get_object_or_404(Associado, pk=pk_associado, organizacao=organizacao)

    associado.aprovado = True
    associado.save()

    return redirect('cursos:painel_instrutor')


@login_required
def gerir_curso_form(request, pk=None):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except Organizacao.DoesNotExist:
        return HttpResponseForbidden("Acesso negado.")

    curso = None
    if pk:
        curso = get_object_or_404(Curso, pk=pk, organizacao=organizacao)

    if request.method == 'POST':
        form = CursoForm(request.POST, request.FILES, instance=curso, organizacao=organizacao)
        if form.is_valid():
            curso_salvo = form.save(commit=False)
            if not curso_salvo.pk:
                curso_salvo.organizacao = organizacao
                curso_salvo.instrutor = request.user
            curso_salvo.save()
            form.save_m2m()
            return redirect('cursos:painel_instrutor')
    else:
        form = CursoForm(instance=curso, organizacao=organizacao)

    context = {
        'form': form,
        'curso': curso,
    }
    return render(request, 'cursos/curso_form.html', context=context)


@login_required
def gerir_aulas(request, pk_curso):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except Organizacao.DoesNotExist:
        return HttpResponseForbidden("Acesso negado.")

    curso = get_object_or_404(Curso, pk=pk_curso, organizacao=organizacao)
    aulas = Aula.objects.filter(curso=curso).order_by('ordem')

    contexto = {
        'curso': curso,
        'aulas': aulas,
    }
    return render(request, 'cursos/gerir_aulas.html', contexto)


@login_required
def aula_form(request, pk_curso, pk_aula=None):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except Organizacao.DoesNotExist:
        return HttpResponseForbidden("Acesso negado.")

    curso = get_object_or_404(Curso, pk=pk_curso, organizacao=organizacao)
    aula = None
    if pk_aula:
        aula = get_object_or_404(Aula, pk=pk_aula, curso=curso)

    if request.method == 'POST':
        form = AulaForm(request.POST, request.FILES, instance=aula)
        if form.is_valid():
            aula_salva = form.save(commit=False)
            aula_salva.curso = curso
            aula_salva.save()
            return redirect('cursos:gerir_aulas', pk_curso=curso.pk)
    else:
        form = AulaForm(instance=aula)

    context = {
        'form': form,
        'curso': curso
    }
    return render(request, 'cursos/aula_form.html', context=context)


@login_required
def apagar_aula(request, pk_aula):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except Organizacao.DoesNotExist:
        return HttpResponseForbidden("Acesso negado.")

    aula = get_object_or_404(Aula, pk=pk_aula, curso__organizacao=organizacao)
    pk_curso = aula.curso.pk

    if request.method == 'POST':
        aula.delete()
        return redirect('cursos:gerir_aulas', pk_curso=pk_curso)

    context = {
        'aula': aula,
    }

    return render(request, 'cursos/aula_confirm_delete.html', context=context)


@login_required
def gerir_categorias(request):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except Organizacao.DoesNotExist:
        return HttpResponseForbidden("Acesso negado.")

    categorias = Categoria.objects.filter(organizacao=organizacao)

    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            nova_categoria = form.save(commit=False)
            nova_categoria.organizacao = organizacao
            nova_categoria.save()
            return redirect('cursos:gerir_categorias')
    else:
        form = CategoriaForm()

    context = {
        'categorias': categorias,
        'form': form
    }
    return render(request, 'cursos/gerir_categorias.html', context=context)


@login_required
def editar_categoria(request, pk_categoria):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except:
        return HttpResponseForbidden('Acesso negado.')

    categoria = get_object_or_404(Categoria, pk=pk_categoria, organizacao=organizacao)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('cursos:gerir_categorias')
    else:
        form = CategoriaForm(instance=categoria)

    context = {
        'form': form,
        'categoria': categoria,
    }

    return render(request, 'cursos/editar_categoria.html', context=context)


@login_required
def apagar_categoria(request, pk_categoria):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except:
        return HttpResponseForbidden('Acesso negado.')

    categoria = get_object_or_404(Categoria, pk=pk_categoria, organizacao=organizacao)

    if request.method == 'POST':
        categoria.delete()
        return redirect('cursos:gerir_categorias')

    context = {
        'categoria': categoria,
    }

    return render(request, 'cursos/apagar_categoria.html', context=context)


@login_required
def lista_topicos(request):
    organizacao_usuario = get_user_organization(request)
    if not organizacao_usuario:
        return render(request, 'cursos/erro_permissao.html')

    if request.method == 'POST':
        form = TopicoDiscussaoForm(request.POST)
        if form.is_valid():
            novo_topico = form.save(commit=False)
            novo_topico.organizacao = organizacao_usuario
            novo_topico.autor = request.user
            novo_topico.save()
            return redirect('cursos:detalhe_topico', pk_topico=novo_topico.pk)
    else:
        form = TopicoDiscussaoForm()

    topicos = TopicoDiscussao.objects.filter(organizacao=organizacao_usuario)

    context = {
        'topicos': topicos,
        'form': form,
    }

    return render(request, 'cursos/lista_topicos.html', context=context)


@login_required
def detalhe_topico(request, pk_topico):
    organizacao_usuario = get_user_organization(request)
    if not organizacao_usuario:
        return render(request, 'cursos/erro_permissao.html')

    topico = get_object_or_404(TopicoDiscussao, pk=pk_topico, organizacao=organizacao_usuario)

    if request.method == 'POST':
        form_comentario = ComentarioTopicoForm(request.POST, request.FILES)
        if form_comentario.is_valid():
            novo_comentario = form_comentario.save(commit=False)
            novo_comentario.topico = topico
            novo_comentario.autor = request.user
            novo_comentario.save()
            return redirect('cursos:detalhe_topico', pk_topico=topico.pk)
    else:
        form_comentario = ComentarioTopicoForm()

    context = {
        'topico': topico,
        'form_comentario': form_comentario,
    }

    return render(request, 'cursos/detalhe_topico.html', context=context)


@login_required
def inscrever_curso(request, pk_curso):
    curso = get_object_or_404(Curso, pk=pk_curso)
    associado = get_object_or_404(Associado, usuario=request.user)

    if curso in associado.cursos_inscritos.all():
        associado.cursos_inscritos.remove(curso)
    else:
        associado.cursos_inscritos.add(curso)

    return redirect('cursos:detalhe_curso', pk=curso.pk)


@login_required
def gerir_quiz_curso(request, pk_curso):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except Organizacao.DoesNotExist:
        return HttpResponseForbidden('Acesso negado.')

    curso = get_object_or_404(Curso, pk=pk_curso, organizacao=organizacao)
    quiz = Quiz.objects.filter(curso=curso).first()

    if request.method == 'POST':
        if not quiz:
            Quiz.objects.create(curso=curso, titulo=f'Avaliação do curso {curso.titulo}')
            return redirect('cursos:gerir_quiz_curso', pk_curso=curso.pk)

    contexto = {
        'curso': curso,
        'quiz': quiz,
    }
    return render(request, 'cursos/gerir_quiz_curso.html', contexto)


@login_required
def pergunta_quiz_form(request, pk_curso, pk_pergunta=None):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except:
        return HttpResponseForbidden('Acesso negado.')

    curso = get_object_or_404(Curso, pk=pk_curso, organizacao=organizacao)
    quiz = get_object_or_404(Quiz, curso=curso)

    pergunta=None
    if pk_pergunta:
        pergunta = get_object_or_404(PerguntaQuiz, pk=pk_pergunta, quiz=quiz)

    if request.method == 'POST':
        form = PerguntaQuizForm(request.POST, instance=pergunta)
        if form.is_valid():
            nova_pergunta = form.save(commit=False)
            nova_pergunta.quiz = quiz
            nova_pergunta.save()
            return redirect('cursos:gerir_opcoes_pergunta', pk_pergunta=nova_pergunta.pk)

    else:
        form = PerguntaQuizForm(instance=pergunta)

    context = {
        'form': form,
        'curso': curso,
        'pergunta': pergunta,
    }

    return render(request, 'cursos/pergunta_quiz_form.html', context=context)


@login_required
def gerir_opcoes_pergunta(request, pk_pergunta):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except Organizacao.DoesNotExist:
        return HttpResponseForbidden('Acesso negado.')

    pergunta = get_object_or_404(PerguntaQuiz, pk=pk_pergunta, quiz__curso__organizacao=organizacao)

    if request.method == 'POST':
        form = OpcaoRespostaForm(request.POST)
        if form.is_valid():
            opcoes_existentes = OpcaoResposta.objects.filter(pergunta=pergunta)
            if opcoes_existentes.count() >= 4:
                messages.error(request, 'Uma pergunta não pode ter mais de 4 opções.')
            else:
                if form.cleaned_data['correta']:
                    opcoes_existentes.update(correta=False)

                nova_opcao = form.save(commit=False)
                nova_opcao.pergunta = pergunta
                nova_opcao.save()
                messages.success(request, 'Opção adicionada com sucesso!')
                return redirect('cursos:gerir_opcoes_pergunta', pk_pergunta=pergunta.pk)
    else:
        form = OpcaoRespostaForm()

    opcoes = OpcaoResposta.objects.filter(pergunta=pergunta)
    context = {
        'pergunta': pergunta,
        'opcoes': opcoes,
        'form': form,
    }
    return render(request, 'cursos/gerir_opcoes_pergunta.html', context=context)


@login_required
def editar_opcao_resposta(request, pk_opcao):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except Organizacao.DoesNotExist:
        return HttpResponseForbidden('Acesso negado.')

    opcao = get_object_or_404(OpcaoResposta, pk=pk_opcao, pergunta__quiz__curso__organizacao=organizacao)
    pergunta = opcao.pergunta

    if request.method == 'POST':
        form = OpcaoRespostaForm(request.POST, instance=opcao)
        if form.is_valid():
            if form.cleaned_data['correta']:
                pergunta.opcoes.exclude(pk=opcao.pk).update(correta=False)

            form.save()
            messages.success(request, 'Opção atualizada com sucesso!')
            return redirect('cursos:gerir_opcoes_pergunta', pk_pergunta=pergunta.pk)
    else:
        form = OpcaoRespostaForm(instance=opcao)

    context = {
        'form': form,
        'pergunta': pergunta,
    }
    return render(request, 'cursos/editar_opcao_resposta.html', context=context)


@login_required
def apagar_opcao_resposta(request, pk_opcao):
    try:
        organizacao = Organizacao.objects.get(dono=request.user)
    except Organizacao.DoesNotExist:
        return HttpResponseForbidden('Acesso negado.')

    opcao = get_object_or_404(OpcaoResposta, pk=pk_opcao, pergunta__quiz__curso__organizacao=organizacao)
    pergunta = opcao.pergunta

    if request.method == 'POST':
        opcao.delete()
        messages.success(request, 'Opção apagada com sucesso!')
        return redirect('cursos:gerir_opcoes_pergunta', pk_pergunta=pergunta.pk)

    context = {
        'opcao': opcao,
        'pergunta': pergunta,
    }
    return render(request, 'cursos/apagar_opcao_resposta.html', context=context)