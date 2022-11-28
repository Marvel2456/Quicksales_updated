from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default = False)
    is_sub_admin = models.BooleanField(default = False)
    is_work_staff = models.BooleanField(default = False)
    phone_number = models.CharField(max_length = 100)
    address = models.CharField(max_length = 200)
    date_created = models.DateTimeField(auto_now_add=True)

class LoggedIn(models.Model):
    staff = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add = True)
    login_id = models.CharField(max_length = 100)

    def __str__(self):
        return str(self.staff)

# class LoggedOut(models.Model):
#     staff = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
#     timestamp = models.DateTimeField(auto_now_add = True)
#     logout_id = models.CharField(max_length = 100)

#     def __str__(self):
#         return str(self.staff)


class ErrorTicket(models.Model):
    staff = models.ForeignKey(CustomUser, on_delete= models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title