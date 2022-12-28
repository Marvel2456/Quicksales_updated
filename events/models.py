# from django.db import models
# from ims.models import Sale, SalesItem

# # Create your models here.

# class Event(models.Model):
#     sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, blank=True, null=True)
#     event_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return str(self.sale.staff)
