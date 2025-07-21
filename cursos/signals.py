from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Resposta, Pergunta, Notificacao


@receiver(post_save, sender=Resposta)
def criar_notificacao_de_resposta(sender, instance, created, **kwargs):
    if created:
        pergunta = instance.pergunta
        autor_da_resposta_atual = instance.usuario
        participantes = {pergunta.usuario}

        respostas_anteriores = Resposta.objects.filter(pergunta=pergunta)
        for resposta in respostas_anteriores:
            participantes.add(resposta.usuario)

        if autor_da_resposta_atual in participantes:
            participantes.remove(autor_da_resposta_atual)

        for participante in participantes:
            Notificacao.objects.create(
                destinatario=participante,
                resposta=instance
            )


@receiver(post_save, sender=Pergunta)
def criar_notificacao_de_pergunta(sender, instance, created, **kwargs):
    if created:
        instrutor = instance.aula.curso.organizacao.dono

        if instance.usuario != instrutor:
            Notificacao.objects.create(
                destinatario=instrutor,
                pergunta=instance
            )