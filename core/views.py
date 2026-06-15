from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone

from .decorators import admin_required, doctor_required, patient_required
from .forms import (
    DoctorSignUpForm,
    PatientSignUpForm,
    AppointmentBookingForm,
    HealthInsightForm,
    AppointmentStatusForm,
    DoctorProfileUpdateForm,
)
from .models import CustomUser, DoctorProfile, PatientProfile, Appointment, HealthInsight


# ---------------------------------------------------------------------------
# Fallback Health Insights (used when no doctor-authored insights exist)
# ---------------------------------------------------------------------------
DEFAULT_HEALTH_INSIGHTS = [
    {
        'title': 'Importance of Regular Health Checkups',
        'category': 'Prevention',
        'content': (
            'Routine health checkups help detect potential health issues before '
            'they become serious. Regular screenings for blood pressure, '
            'cholesterol, and blood sugar levels allow early intervention and '
            'better long-term outcomes. Schedule an annual checkup with your '
            'physician, even if you feel perfectly healthy, to stay ahead of '
            'any underlying conditions.'
        ),
        'image': '/static/img/insight_checkup.svg',
        'author_name': 'MedSaaS Health Team',
        'created_at': timezone.now(),
    },
    {
        'title': 'Healthy Diet Tips',
        'category': 'Nutrition',
        'content': (
            'A balanced diet rich in fruits, vegetables, whole grains, and lean '
            'proteins is the foundation of good health. Limit processed foods, '
            'added sugars, and excess sodium. Staying hydrated and eating in '
            'moderation can significantly reduce the risk of chronic diseases '
            'such as diabetes and heart disease.'
        ),
        'image': '/static/img/insight_nutrition.svg',
        'author_name': 'MedSaaS Health Team',
        'created_at': timezone.now(),
    },
    {
        'title': 'Benefits of Daily Exercise',
        'category': 'Fitness',
        'content': (
            'Engaging in at least 30 minutes of moderate exercise daily improves '
            'cardiovascular health, strengthens muscles, and boosts mental '
            'wellbeing. Activities like walking, cycling, swimming, or yoga can '
            'be easily incorporated into your daily routine and provide '
            'long-lasting health benefits.'
        ),
        'image': '/static/img/insight_fitness.svg',
        'author_name': 'MedSaaS Health Team',
        'created_at': timezone.now(),
    },
    {
        'title': 'Mental Health Awareness',
        'category': 'Mental Health',
        'content': (
            'Mental health is just as important as physical health. Practicing '
            'mindfulness, maintaining social connections, and seeking '
            'professional support when needed can help manage stress, anxiety, '
            'and depression. Do not hesitate to talk to a healthcare provider '
            'about your mental wellbeing.'
        ),
        'image': '/static/img/insight_mental.svg',
        'author_name': 'MedSaaS Health Team',
        'created_at': timezone.now(),
    },
    {
        'title': 'Preventive Healthcare Tips',
        'category': 'Prevention',
        'content': (
            'Preventive care includes vaccinations, screenings, and lifestyle '
            'changes aimed at avoiding illness before it occurs. Wash your '
            'hands regularly, stay up to date with immunizations, avoid tobacco '
            'use, and maintain a healthy weight to reduce your risk of '
            'developing chronic conditions.'
        ),
        'image': '/static/img/insight_prevention.svg',
        'author_name': 'MedSaaS Health Team',
        'created_at': timezone.now(),
    },
]


# ---------------------------------------------------------------------------
# Public Pages
# ---------------------------------------------------------------------------
def home(request):
    stats = {
        'total_doctors': DoctorProfile.objects.filter(is_approved=True).count(),
        'total_patients': PatientProfile.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'total_specializations': DoctorProfile.objects.filter(is_approved=True)
            .values_list('specialization', flat=True).distinct().count(),
    }
    latest_insights = HealthInsight.objects.all()[:3]
    if not latest_insights:
        latest_insights = DEFAULT_HEALTH_INSIGHTS[:3]

    return render(request, 'core/home.html', {
        'stats': stats,
        'latest_insights': latest_insights,
    })


def health_insights(request):
    category = request.GET.get('category', '')
    search_query = request.GET.get('q', '')

    insights_qs = HealthInsight.objects.all()

    if insights_qs.exists():
        if category:
            insights_qs = insights_qs.filter(category=category)
        if search_query:
            insights_qs = insights_qs.filter(
                Q(title__icontains=search_query) | Q(content__icontains=search_query)
            )
        insights_list = list(insights_qs)
        using_fallback = False
    else:
        insights_list = DEFAULT_HEALTH_INSIGHTS
        if category:
            insights_list = [i for i in insights_list if i['category'] == category]
        if search_query:
            insights_list = [
                i for i in insights_list
                if search_query.lower() in i['title'].lower() or search_query.lower() in i['content'].lower()
            ]
        using_fallback = True

    paginator = Paginator(insights_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = HealthInsight.CATEGORY_CHOICES

    return render(request, 'core/health_insights.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category,
        'search_query': search_query,
        'using_fallback': using_fallback,
    })


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
class MedSaaSLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


def signup_choice(request):
    return render(request, 'registration/signup_choice.html')


def doctor_signup(request):
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                "Registration successful! Your account is pending admin approval. "
                "You will gain full dashboard access once approved."
            )
            return redirect('dashboard_redirect')
    else:
        form = DoctorSignUpForm()

    return render(request, 'registration/signup_doctor.html', {'form': form})


def patient_signup(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to MedSaaS! Your account has been created.")
            return redirect('dashboard_redirect')
    else:
        form = PatientSignUpForm()

    return render(request, 'registration/signup_patient.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


# ---------------------------------------------------------------------------
# Dashboard Redirect
# ---------------------------------------------------------------------------
@login_required
def dashboard_redirect(request):
    user = request.user
    if user.role == 'ADMIN':
        return redirect('admin_dashboard')
    elif user.role == 'DOCTOR':
        try:
            profile = user.doctor_profile
        except DoctorProfile.DoesNotExist:
            profile = DoctorProfile.objects.create(user=user, specialization='General', is_approved=False)
        if not profile.is_approved:
            return redirect('pending_approval')
        return redirect('doctor_dashboard')
    elif user.role == 'PATIENT':
        return redirect('patient_dashboard')
    return redirect('home')


@login_required
def pending_approval(request):
    if request.user.role != 'DOCTOR':
        return redirect('dashboard_redirect')
    try:
        if request.user.doctor_profile.is_approved:
            return redirect('doctor_dashboard')
    except DoctorProfile.DoesNotExist:
        pass
    return render(request, 'core/pending_approval.html')


# ---------------------------------------------------------------------------
# Admin Dashboard
# ---------------------------------------------------------------------------
@admin_required
def admin_dashboard(request):
    kpi = {
        'total_doctors': CustomUser.objects.filter(role='DOCTOR').count(),
        'total_patients': CustomUser.objects.filter(role='PATIENT').count(),
        'total_appointments': Appointment.objects.count(),
        'pending_approvals': DoctorProfile.objects.filter(is_approved=False).count(),
    }

    doctors = CustomUser.objects.filter(role='DOCTOR').select_related('doctor_profile').order_by('-id')
    appointments = Appointment.objects.select_related('patient', 'doctor').all()[:50]

    return render(request, 'core/admin_dashboard.html', {
        'kpi': kpi,
        'doctors': doctors,
        'appointments': appointments,
    })


@admin_required
def admin_approve_doctor(request, doctor_id):
    profile = get_object_or_404(DoctorProfile, user_id=doctor_id)
    profile.is_approved = True
    profile.save()
    messages.success(request, f"Dr. {profile.user.get_full_name() or profile.user.username} has been approved.")
    return redirect('admin_dashboard')


@admin_required
def admin_reject_doctor(request, doctor_id):
    profile = get_object_or_404(DoctorProfile, user_id=doctor_id)
    profile.is_approved = False
    profile.save()
    messages.warning(request, f"Dr. {profile.user.get_full_name() or profile.user.username} approval has been revoked.")
    return redirect('admin_dashboard')


@admin_required
def admin_cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'CANCELLED'
    appointment.save()
    messages.success(request, "Appointment has been cancelled.")
    return redirect('admin_dashboard')


@admin_required
def admin_reassign_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        new_doctor_id = request.POST.get('doctor')
        new_doctor = get_object_or_404(CustomUser, id=new_doctor_id, role='DOCTOR')
        appointment.doctor = new_doctor
        appointment.status = 'PENDING'
        appointment.save()
        messages.success(request, "Appointment has been reassigned successfully.")
    return redirect('admin_dashboard')


# ---------------------------------------------------------------------------
# Doctor Dashboard
# ---------------------------------------------------------------------------
@doctor_required
def doctor_dashboard(request):
    profile = getattr(request.user, 'doctor_profile', None)
    if profile is None or not profile.is_approved:
        return redirect('pending_approval')

    appointments = Appointment.objects.filter(doctor=request.user).select_related('patient', 'patient__patient_profile')
    insights = HealthInsight.objects.filter(doctor=request.user)

    appointment_stats = {
        'pending': appointments.filter(status='PENDING').count(),
        'approved': appointments.filter(status='APPROVED').count(),
        'completed': appointments.filter(status='COMPLETED').count(),
        'cancelled': appointments.filter(status='CANCELLED').count(),
    }

    return render(request, 'core/doctor_dashboard.html', {
        'profile': profile,
        'appointments': appointments,
        'insights': insights,
        'appointment_stats': appointment_stats,
        'status_form': AppointmentStatusForm(),
        'insight_form': HealthInsightForm(),
        'profile_form': DoctorProfileUpdateForm(instance=profile),
    })


@doctor_required
def doctor_update_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    if request.method == 'POST':
        form = AppointmentStatusForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully.")
        else:
            messages.error(request, "Could not update the appointment. Please check the form.")
    return redirect('doctor_dashboard')


@doctor_required
def doctor_update_profile(request):
    profile = getattr(request.user, 'doctor_profile', None)
    if profile is None:
        return redirect('doctor_dashboard')
    if request.method == 'POST':
        form = DoctorProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
        else:
            messages.error(request, "Could not update profile. Please check the form.")
    return redirect('doctor_dashboard')


@doctor_required
def doctor_insight_create(request):
    profile = getattr(request.user, 'doctor_profile', None)
    if profile is None or not profile.is_approved:
        return redirect('pending_approval')

    if request.method == 'POST':
        form = HealthInsightForm(request.POST, request.FILES)
        if form.is_valid():
            insight = form.save(commit=False)
            insight.doctor = request.user
            insight.save()
            messages.success(request, "Health insight published successfully.")
        else:
            messages.error(request, "Could not publish the insight. Please check the form.")
    return redirect('doctor_dashboard')


@doctor_required
def doctor_insight_update(request, insight_id):
    insight = get_object_or_404(HealthInsight, id=insight_id, doctor=request.user)
    if request.method == 'POST':
        form = HealthInsightForm(request.POST, request.FILES, instance=insight)
        if form.is_valid():
            form.save()
            messages.success(request, "Health insight updated successfully.")
        else:
            messages.error(request, "Could not update the insight. Please check the form.")
    return redirect('doctor_dashboard')


@doctor_required
def doctor_insight_delete(request, insight_id):
    insight = get_object_or_404(HealthInsight, id=insight_id, doctor=request.user)
    insight.delete()
    messages.success(request, "Health insight deleted successfully.")
    return redirect('doctor_dashboard')


# ---------------------------------------------------------------------------
# Patient Dashboard
# ---------------------------------------------------------------------------
@patient_required
def patient_dashboard(request):
    profile = getattr(request.user, 'patient_profile', None)
    appointments = Appointment.objects.filter(patient=request.user).select_related('doctor', 'doctor__doctor_profile')

    upcoming_appointments = appointments.filter(
        status__in=['PENDING', 'APPROVED'],
        date__gte=timezone.now().date()
    ).order_by('date', 'time')

    prescription_history = appointments.filter(
        status='COMPLETED'
    ).exclude(doctor_notes='').exclude(doctor_notes__isnull=True).order_by('-date')

    booking_form = AppointmentBookingForm()

    return render(request, 'core/patient_dashboard.html', {
        'profile': profile,
        'appointments': appointments,
        'upcoming_appointments': upcoming_appointments,
        'prescription_history': prescription_history,
        'booking_form': booking_form,
    })


@patient_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = 'PENDING'
            appointment.save()
            messages.success(request, "Appointment requested successfully! Awaiting doctor approval.")
        else:
            messages.error(request, "Could not book the appointment. Please check the form for errors.")
    return redirect('patient_dashboard')


@patient_required
def cancel_own_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    if appointment.status in ['PENDING', 'APPROVED']:
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.success(request, "Appointment cancelled successfully.")
    else:
        messages.error(request, "This appointment cannot be cancelled.")
    return redirect('patient_dashboard')
