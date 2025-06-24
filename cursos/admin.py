from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Associado, Curso, Aula


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


class AulaInline(admin.TabularInline):
    model = Aula
    extra = 1


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'instrutor', 'data_criacao')
    search_fields = ('titulo', 'descricao')
    inlines = [AulaInline]


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'curso', 'ordem')
    list_filter = ('curso',)
    search_fields = ('titulo', 'descricao')
