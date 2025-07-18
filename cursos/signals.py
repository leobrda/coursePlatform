from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Resposta, Pergunta, Notificacao


@receiver(post_save, sender=Resposta)
def criar_notificacao_de_resposta(sender, instance, created, **kwargs):
    if created:
        pergunta = instance.pergunta
        autor_pergunta = pergunta.usuario

        if instance.usuario != autor_pergunta:
            Notificacao.objects.create(
                destinatario=autor_pergunta,
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