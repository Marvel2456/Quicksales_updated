from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from account.models import CustomUser
# from .signals import view_object

# Create your models here.

class History(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    viewed_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.content_type)
    
    class Meta:
        verbose_name_plural = "Histories"

def viewd_object_receiver(sender, instance, request, **kwargs):
    audit_history = History.objects.create(
        user = request.user,
        content_type = ContentType.objects.get_for_model(sender),
        object_id = instance.id,
    )
# view_object.connect(viewd_object_receiver)