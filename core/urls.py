from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('health-insights/', views.health_insights, name='health_insights'),

    # Authentication
    path('login/', views.MedSaaSLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_choice, name='signup_choice'),
    path('signup/doctor/', views.doctor_signup, name='signup_doctor'),
    path('signup/patient/', views.patient_signup, name='signup_patient'),

    # Dashboard redirect & pending approval
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('pending-approval/', views.pending_approval, name='pending_approval'),

    # Admin dashboard
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/approve-doctor/<int:doctor_id>/', views.admin_approve_doctor, name='admin_approve_doctor'),
    path('dashboard/admin/reject-doctor/<int:doctor_id>/', views.admin_reject_doctor, name='admin_reject_doctor'),
    path('dashboard/admin/cancel-appointment/<int:appointment_id>/', views.admin_cancel_appointment, name='admin_cancel_appointment'),
    path('dashboard/admin/reassign-appointment/<int:appointment_id>/', views.admin_reassign_appointment, name='admin_reassign_appointment'),

    # Doctor dashboard
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('dashboard/doctor/appointment/<int:appointment_id>/update/', views.doctor_update_appointment, name='doctor_update_appointment'),
    path('dashboard/doctor/profile/update/', views.doctor_update_profile, name='doctor_update_profile'),
    path('dashboard/doctor/insight/create/', views.doctor_insight_create, name='doctor_insight_create'),
    path('dashboard/doctor/insight/<int:insight_id>/update/', views.doctor_insight_update, name='doctor_insight_update'),
    path('dashboard/doctor/insight/<int:insight_id>/delete/', views.doctor_insight_delete, name='doctor_insight_delete'),

    # Patient dashboard
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/patient/book/', views.book_appointment, name='book_appointment'),
    path('dashboard/patient/appointment/<int:appointment_id>/cancel/', views.cancel_own_appointment, name='cancel_own_appointment'),

    # Password reset (uses Django defaults with our templates)
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
]
