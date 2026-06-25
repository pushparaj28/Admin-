from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['booking_id', 'patient_name', 'email', 'appointment_date', 'appointment_time', 'status']
        
        # Widgets ka use karke hum form input me CSS classes aur types add kar rahe hain
        widgets = {
            'booking_id': forms.TextInput(attrs={'class': 'input-box', 'placeholder': 'e.g. BK-101'}),
            'patient_name': forms.TextInput(attrs={'class': 'input-box', 'placeholder': 'Bhaiya Name Dalo Yaha per'}),
            'email': forms.EmailInput(attrs={'class': 'input-box', 'placeholder': 'Email Address'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'input-box'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time', 'class': 'input-box'}),
            'status': forms.Select(attrs={'class': 'input-box'}),
        }