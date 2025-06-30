from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Associado, Curso, Aula, Pergunta, Resposta, Categoria
from urllib.parse import urlparse, parse_qs


class AssociadoInline(admin.StackedInline):
    model = Associado
    can_delete = False
    verbose_name_plural = 'Associados'


class UserAdmin(BaseUserAdmin):
    inlines = (AssociadoInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_aprovado')

    def get_aprovado(self, instance):
        return instance.associado.aprovado

    get_aprovado.boolean = True
    get_aprovado.short_description = 'Cadastro Aprovado'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class AulaAdminForm(forms.ModelForm):
    video_url = forms.URLField(label="URL do Vídeo no YouTube", required=False,
                               help_text="Cole a URL completa do vídeo do YouTube aqui.")

    class Meta:
        model = Aula
        fields = ['curso', 'titulo', 'descricao', 'video_url', 'material_apoio', 'ordem']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.youtube_video_id:
            self.fields['video_url'].initial = f"https://www.youtube.com/watch?v={self.instance.youtube_video_id}"

    def clean_video_url(self):
        url = self.cleaned_data.get('video_url')
        if not url:
            return ''

        try:
            parsed_url = urlparse(url)
            if 'youtube.com' in parsed_url.netloc:
                query = parse_qs(parsed_url.query)
                # O ID do vídeo é o valor do parâmetro 'v'
                return query.get('v', [None])[0]
            elif 'youtu.be' in parsed_url.netloc:
                # Em URLs encurtadas, o ID é o caminho
                return parsed_url.path.lstrip('/')
        except Exception:
            pass

        raise forms.ValidationError("URL do YouTube inválida ou não reconhecida.")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.youtube_video_id = self.cleaned_data.get('video_url') or ''

        if commit:
            instance.save()
        return instance


class AulaInline(admin.TabularInline):
    model = Aula
    form = AulaAdminForm
    extra = 1


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'instrutor', 'data_criacao')
    search_fields = ('titulo', 'descricao')
    filter_horizontal = ('categorias',)
    inlines = [AulaInline]


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'curso', 'ordem')
    list_filter = ('curso',)
    search_fields = ('titulo', 'descricao')


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('id', 'aula', 'usuario', 'data_criacao')
    list_filter = ('aula',)
    search_fields = ('conteudo',)


@admin.register(Resposta)
class RespostaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pergunta', 'usuario', 'data_criacao')
    list_filter = ('pergunta__aula',)
    search_fields = ('conteudo',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    readonly_fields = ('slug',)