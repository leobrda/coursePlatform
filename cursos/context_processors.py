from .models import Notificacao, Organizacao


def unread_notifications(request):
    contexto = {}
    if request.user.is_authenticated:
        contexto['unread_notification_count'] = Notificacao.objects.filter(destinatario=request.user,
                                                                           lida=False).count()

        contexto['is_org_owner'] = Organizacao.objects.filter(dono=request.user).exists()

        return contexto
    return {}

