from .models import Notificacao

def unread_notifications(request):
    if request.user.is_authenticated:
        count = Notificacao.objects.filter(destinatario=request.user, lida=False).count()
        return {'unread_notification_count': count}
    return {}