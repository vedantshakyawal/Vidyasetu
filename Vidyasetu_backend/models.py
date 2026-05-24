from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10,choices=ROLE_CHOICES,default='student')
    department = models.CharField(max_length=100, blank=True, null=True)
    roll_no = models.CharField(max_length=50 , blank= True , null=True)

    def __str__(self):
        return f"{self.username}({self.get_role_display()})"
    