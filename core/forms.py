from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import DoctorProfile, PatientProfile, Appointment, HealthInsight

User = get_user_model()


BASE_INPUT_CLASS = 'form-control'
BASE_SELECT_CLASS = 'form-select'


class DoctorSignUpForm(UserCreationForm):
    """
    Registration form for new doctors. Creates a CustomUser with role=DOCTOR
    and an associated DoctorProfile (pending approval by default).
    """
    first_name = forms.CharField(max_length=150, required=True,
                                  widget=forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=150, required=True,
                                 widget=forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'placeholder': 'Last name'}))
    email = forms.EmailField(required=True,
                              widget=forms.EmailInput(attrs={'class': BASE_INPUT_CLASS, 'placeholder': 'Email address'}))
    specialization = forms.CharField(max_length=120, required=True,
                                      widget=forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'placeholder': 'e.g. Cardiology'}))
    experience_years = forms.IntegerField(min_value=0, required=True,
                                           widget=forms.NumberInput(attrs={'class': BASE_INPUT_CLASS, 'placeholder': 'Years of experience'}))
    phone = forms.CharField(max_length=20, required=True,
                             widget=forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'placeholder': 'Phone number'}))
    profile_picture = forms.ImageField(required=False,
                                        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'specialization', 'experience_years', 'phone', 'profile_picture',
            'password1', 'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': BASE_INPUT_CLASS, 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': BASE_INPUT_CLASS, 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': BASE_INPUT_CLASS, 'placeholder': 'Confirm password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'DOCTOR'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            DoctorProfile.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                experience_years=self.cleaned_data['experience_years'],
                phone=self.cleaned_data['phone'],
                profile_picture=self.cleaned_data.get('profile_picture'),
                is_approved=False,
            )
        return user


class PatientSignUpForm(UserCreationForm):
    """
    Registration form for new patients. Creates a CustomUser with role=PATIENT
    and an associated PatientProfile.
    """
    first_name = forms.CharField(max_length=150, required=True,
                                  widget=forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=150, required=True,
                                 widget=forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'placeholder': 'Last name'}))
    email = forms.EmailField(required=True,
                              widget=forms.EmailInput(attrs={'class': BASE_INPUT_CLASS, 'placeholder': 'Email address'}))
    age = forms.IntegerField(min_value=0, required=True,
                              widget=forms.NumberInput(attrs={'class': BASE_INPUT_CLASS, 'placeholder': 'Age'}))
    gender = forms.ChoiceField(choices=PatientProfile.GENDER_CHOICES, required=True,
                                widget=forms.Select(attrs={'class': BASE_SELECT_CLASS}))
    phone = forms.CharField(max_length=20, required=True,
                             widget=forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'placeholder': 'Phone number'}))
    address = forms.CharField(required=True,
                               widget=forms.Textarea(attrs={'class': BASE_INPUT_CLASS, 'rows': 3, 'placeholder': 'Address'}))

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'age', 'gender', 'phone', 'address',
            'password1', 'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': BASE_INPUT_CLASS, 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': BASE_INPUT_CLASS, 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': BASE_INPUT_CLASS, 'placeholder': 'Confirm password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'PATIENT'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                age=self.cleaned_data['age'],
                gender=self.cleaned_data['gender'],
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address'],
            )
        return user


class AppointmentBookingForm(forms.ModelForm):
    """
    Booking wizard form used by patients. Allows filtering of doctors
    by specialization via the `specialization` field, which is not saved
    directly but used to narrow the doctor queryset in the view/template.
    """
    specialization = forms.ChoiceField(required=False, label="Filter by Specialization",
                                        widget=forms.Select(attrs={'class': BASE_SELECT_CLASS, 'id': 'id_specialization'}))

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'symptoms_description']
        widgets = {
            'doctor': forms.Select(attrs={'class': BASE_SELECT_CLASS, 'id': 'id_doctor'}),
            'date': forms.DateInput(attrs={'class': BASE_INPUT_CLASS, 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': BASE_INPUT_CLASS, 'type': 'time'}),
            'symptoms_description': forms.Textarea(attrs={'class': BASE_INPUT_CLASS, 'rows': 4, 'placeholder': 'Describe your symptoms...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        specializations = (
            DoctorProfile.objects.filter(is_approved=True)
            .values_list('specialization', flat=True)
            .distinct()
            .order_by('specialization')
        )
        self.fields['specialization'].choices = [('', 'All Specializations')] + [
            (s, s) for s in specializations
        ]

        self.fields['doctor'].queryset = User.objects.filter(
            role='DOCTOR', doctor_profile__is_approved=True
        ).order_by('first_name', 'last_name')

        self.fields['doctor'].label_from_instance = lambda obj: (
            f"Dr. {obj.get_full_name() or obj.username} "
            f"({obj.doctor_profile.specialization})"
        )


class HealthInsightForm(forms.ModelForm):
    """
    Form used by doctors to create or update Health Insight articles.
    """
    class Meta:
        model = HealthInsight
        fields = ['title', 'content', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'placeholder': 'Insight title'}),
            'content': forms.Textarea(attrs={'class': BASE_INPUT_CLASS, 'rows': 6, 'placeholder': 'Write the full content here...'}),
            'category': forms.Select(attrs={'class': BASE_SELECT_CLASS}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class AppointmentStatusForm(forms.ModelForm):
    """
    Used by doctors/admins to update appointment status and add notes.
    """
    class Meta:
        model = Appointment
        fields = ['status', 'doctor_notes']
        widgets = {
            'status': forms.Select(attrs={'class': BASE_SELECT_CLASS}),
            'doctor_notes': forms.Textarea(attrs={'class': BASE_INPUT_CLASS, 'rows': 4, 'placeholder': 'Medical notes / prescription details...'}),
        }


class DoctorProfileUpdateForm(forms.ModelForm):
    """
    Allows a doctor to update their own profile details.
    """
    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'experience_years', 'phone', 'profile_picture']
        widgets = {
            'specialization': forms.TextInput(attrs={'class': BASE_INPUT_CLASS}),
            'experience_years': forms.NumberInput(attrs={'class': BASE_INPUT_CLASS}),
            'phone': forms.TextInput(attrs={'class': BASE_INPUT_CLASS}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
