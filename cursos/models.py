from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models import Count
from django.db.models.functions import Coalesce


class Associado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuário')
    biografia = models.TextField(blank=True, verbose_name='Biografia')
    aprovado = models.BooleanField(default=False, verbose_name='Cadastro Aprovado')
    aulas_concluidas = models.ManyToManyField('Aula', related_name='concluida_por', blank=True)

    def __str__(self):
        return self.usuario.username


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=100, unique=True, blank=True, help_text="Este campo é preenchido automaticamente.")

    class Meta:
        verbose_name_plural = "Categorias"
        ordering = ['nome']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Curso(models.Model):
    titulo = models.CharField(max_length=350, verbose_name='Título do Curso')
    descricao = models.TextField(verbose_name='Descrição do Curso', blank=True)
    imagem_capa = models.ImageField(upload_to='cursos/capas/', blank=True, null=True, verbose_name='Imagem de Capa')
    instrutor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Instrutor')
    categorias = models.ManyToManyField(Categoria, related_name='cursos', blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo


class Aula(models.Model):
    curso = models.ForeignKey(Curso, related_name='aulas', on_delete=models.CASCADE, verbose_name='Curso')
    titulo = models.CharField(max_length=350, verbose_name='Título da Aula')
    descricao = models.TextField(verbose_name='Descrição da Aula')
    youtube_video_id = models.CharField(
        max_length=100,
        verbose_name='ID do vídeo no Youtube',
        help_text='Cole aqui apenas o código do vídeo, não a URL completa. Ex: dQw4w9WgXcQ'
    )
    material_apoio = models.FileField(upload_to='cursos/materiais/', verbose_name='Material de Apoio', blank=True, null=True)
    ordem = models.PositiveIntegerField(verbose_name='Ordem')

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f'{self.curso.titulo} - Aula {self.ordem}: {self.titulo}'


class Pergunta(models.Model):
    aula = models.ForeignKey(Aula, related_name='perguntas', on_delete=models.CASCADE, verbose_name="Aula")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    conteudo = models.TextField(verbose_name="Conteúdo da Pergunta")
    data_criacao = models.DateTimeField(auto_now_add=True)

    def get_respostas_ordenadas(self):
        return self.respostas.annotate(
            num_votos=Coalesce(Count('votos'), 0)
        ).order_by('-num_votos', 'data_criacao')

    class Meta:
        ordering = ['data_criacao']

    def __str__(self):
        return f'Pergunta de {self.usuario.username} na aula "{self.aula.titulo}"'


class Resposta(models.Model):
    pergunta = models.ForeignKey(Pergunta, related_name='respostas', on_delete=models.CASCADE, verbose_name="Pergunta")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    conteudo = models.TextField(verbose_name="Conteúdo da Resposta")
    data_criacao = models.DateTimeField(auto_now_add=True)
    votos = models.ManyToManyField(User, related_name='respostas_votadas', blank=True, verbose_name="Votos")

    class Meta:
        ordering = ['data_criacao']

    def __str__(self):
        return f'Resposta de {self.usuario.username} à pergunta "{self.pergunta.id}"'

    def total_votos(self):
        return self.votos.count()


class Notificacao(models.Model):
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    resposta = models.ForeignKey(Resposta, on_delete=models.CASCADE)
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name_plural = 'Notificações'

    def __str__(self):
        return f'Notificação para {self.destinatario.username} sobre a resposta {self.resposta.id}'