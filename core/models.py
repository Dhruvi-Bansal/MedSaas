from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    """
    Custom user model with role-based access control.
    Roles: ADMIN, DOCTOR, PATIENT
    """
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PATIENT')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        return self.role == 'ADMIN'

    @property
    def is_doctor_role(self):
        return self.role == 'DOCTOR'

    @property
    def is_patient_role(self):
        return self.role == 'PATIENT'


class DoctorProfile(models.Model):
    """
    Extended profile information for users with the DOCTOR role.
    Doctors must be approved by an admin before gaining dashboard access.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=120)
    experience_years = models.PositiveIntegerField(default=0)
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(
        upload_to='doctor_profiles/',
        blank=True,
        null=True
    )
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.specialization}"

    @property
    def display_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/img/default_doctor.svg'


class PatientProfile(models.Model):
    """
    Extended profile information for users with the PATIENT role.
    """
    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} (Patient)"


class Appointment(models.Model):
    """
    Represents a booking made by a patient with a doctor.
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    patient = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='patient_appointments',
        limit_choices_to={'role': 'PATIENT'}
    )
    doctor = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'DOCTOR'}
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    symptoms_description = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True, null=True, help_text="Medical notes / prescription added by the doctor")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.patient.username} -> {self.doctor.username} on {self.date} at {self.time}"

    @property
    def status_badge_class(self):
        mapping = {
            'PENDING': 'badge-pending',
            'APPROVED': 'badge-approved',
            'COMPLETED': 'badge-completed',
            'CANCELLED': 'badge-cancelled',
        }
        return mapping.get(self.status, 'badge-pending')


class HealthInsight(models.Model):
    """
    Health articles / insights authored by doctors and shown publicly.
    If no doctor-authored insights exist, the view layer renders system
    default fallback cards instead.
    """
    CATEGORY_CHOICES = (
        ('Nutrition', 'Nutrition'),
        ('Fitness', 'Fitness'),
        ('Mental Health', 'Mental Health'),
        ('Diseases', 'Diseases'),
        ('Prevention', 'Prevention'),
        ('Lifestyle', 'Lifestyle'),
    )

    doctor = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        related_name='health_insights',
        null=True, blank=True,
        limit_choices_to={'role': 'DOCTOR'}
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Lifestyle')
    image = models.ImageField(upload_to='health_insights/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def display_image_url(self):
        if self.image:
            return self.image.url
        return '/static/img/default_insight.svg'

    @property
    def author_name(self):
        if self.doctor:
            return f"Dr. {self.doctor.get_full_name() or self.doctor.username}"
        return "MedSaaS Health Team"
