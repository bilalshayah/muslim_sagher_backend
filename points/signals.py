# points/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserPoints

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_points(sender, instance, created, **kwargs):
    """
    ينشئ سجل UserPoints تلقائيًا عند إنشاء أي مستخدم جديد.
    - يعمل مع CustomUser أو أي موديل مستخدم مخصص.
    - يمنع تكرار السجلات لأن UserPoints يجب أن يكون OneToOneField.
    """
    if created:
        # إنشاء سجل UserPoints جديد بقيم افتراضية
        UserPoints.objects.create(user=instance)