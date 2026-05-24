from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    
    CLASS_CHOICES = (
        ('11th', '11th'),
        ('12th', '12th'),
    )

    # Core Identity
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    # Faculty/Admin Specific
    department = models.CharField(max_length=100, blank=True, null=True)
    
    # Student Specific
    roll_no = models.CharField(max_length=50, blank=True, null=True)
    student_class = models.CharField(max_length=10, choices=CLASS_CHOICES, blank=True, null=True)
    course = models.CharField(max_length=50, blank=True, null=True)  # e.g., 'PCMB', 'PCMC'
    
    # Security: Single Session Tracking
    device_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    