from django import forms
from django.contrib.auth.models import User
from .models import Associado, Pergunta, Resposta, Organizacao, Curso, Categoria, Aula, TopicoDiscussao, ComentarioTopico
import re


class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(label='Nome', max_length=150, required=True)
    last_name = forms.CharField(label='Sobrenome', max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)
    biografia = forms.CharField(label='Biografia', widget=forms.Textarea, required=False)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Seha', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        self.organizacao = kwargs.pop('organizacao', None)
        super().__init__(*args, **kwargs)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('As senhas não conferem.')
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            Associado.objects.create(
                usuario=user,
                organizacao=self.organizacao,
                biografia=self.cleaned_data.get('biografia', '')
            )
        return user


class UserEditForm(forms.ModelForm):
    biografia = forms.CharField(label='Biografia', widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(self.instance, 'associado'):
            self.fields['biografia'].initial = self.instance.associado.biografia

    def save(self, commit=True):
        user = super().save(commit=commit)

        if hasattr(user, 'associado'):
            user.associado.biografia = self.cleaned_data['biografia']
            if commit:
                user.associado.save()

        return user


class PerguntaForm(forms.ModelForm):
    class Meta:
        model = Pergunta
        fields = ['conteudo']
        widgets = {
            'conteudo': forms.Textarea(attrs={'placeholder': 'Digite sua pergunta aqui...', 'rows': 4}),
        }
        labels = {
            'conteudo': 'Sua Pergunta'
        }


class RespostaForm(forms.ModelForm):
    class Meta:
        model = Resposta
        fields = ['conteudo']
        widgets = {
            'conteudo': forms.Textarea(attrs={'placeholder': 'Digite sua resposta...', 'rows': 3}),
        }
        labels = {
            'conteudo': ''
        }


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['titulo', 'descricao', 'imagem_capa', 'categorias']
        widgets = {
            'categorias': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        organizacao = kwargs.pop('organizacao', None)
        super().__init__(*args, **kwargs)
        if organizacao:
            self.fields['categorias'].queryset = Categoria.objects.filter(organizacao=organizacao)


class AulaForm(forms.ModelForm):
    video_url = forms.CharField(
        label='URL do vídeo no Youtube',
        help_text='Cole a URL completa do vídeo do Youtube aqui. O sistema extrairá o ID automaticamente.',
        required=True
    )
    class Meta:
        model = Aula
        fields = ['titulo', 'descricao', 'video_url', 'material_apoio', 'ordem']

    def clean_video_url(self):
        url = self.cleaned_data.get('video_url')
        if url:
            regex = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
            match = re.search(regex, url)
            if match:
                return match.group(1)
            else:
                raise forms.ValidationError("URL do YouTube inválida ou formato não reconhecido.")
        return url

    def save(self, commit=True):
        self.instance.youtube_video_id = self.cleaned_data.get('video_url')
        return super().save(commit=commit)


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']


class TopicoDiscussaoForm(forms.ModelForm):
    class Meta:
        model = TopicoDiscussao
        fields = ['titulo', 'conteudo']
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Qual o título do tópico?'}),
            'conteudo': forms.Textarea(attrs={'rows': 15, 'placeholder': 'Comece o tópico aqui...'}),
        }
        labels = {
            'titulo': 'Título',
            'conteudo': 'Conteúdo do Tópico'
        }


class ComentarioTopicoForm(forms.ModelForm):
    class Meta:
        model = ComentarioTopico
        fields = ['conteudo', 'arquivo_anexo']
        widgets = {
            'conteudo': forms.Textarea(attrs={'rows': 15, 'placeholder': 'Adicione o seu comentário...'}),
        }
        labels = {
            'conteudo': 'Seu comentário',
            'arquivo_anexo': 'Anexar um Ficheiro (Opcional)'
        }
