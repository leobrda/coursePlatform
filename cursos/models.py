from django.db import models
from django.contrib.auth.models import User


class Associado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuário')
    biografia = models.TextField(blank=True, verbose_name='Biografia')
    aprovado = models.BooleanField(default=False, verbose_name='Cadastro Aprovado')

    def __str__(self):
        return self.usuario.username


class Curso(models.Model):
    titulo = models.CharField(max_length=350, verbose_name='Título do Curso')
    descricao = models.TextField(verbose_name='Descrição do Curso', blank=True)
    imagem_capa = models.ImageField(upload_to='cursos/capas/', blank=True, null=True, verbose_name='Imagem de Capa')
    instrutor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Instrutor')
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
