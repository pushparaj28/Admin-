from django import forms
from .models import Appointment
from .models import Review
from .models import Review, PayoutEarning

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment

        # hide kar dega ye is input ko  
        exclude = ['booking_id'] 
        
        # ---> YAHAN MAGIC HAI: Django ko batana ki kaunsa input kaisa dikhega <---
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            # Status ke liye premium dropdown class
            if field_name == 'status':
                field.widget.attrs['class'] = 'custom-status-select'
            
            # Baaki sabhi fields ke liye premium input box class
            else:
                # Pehle se maujood classes (jaise date/time) ko bina hataye nayi class jodna
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{existing_classes} input-box'.strip()


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['patient_name', 'rating', 'review_text', 'is_verified_patient']
        
        # UI ko sundar banane ke liye thodi classes add kar dete hain
        widgets = {
            'patient_name': forms.TextInput(attrs={'class': 'input-box', 'placeholder': 'E.g.Pushpendra Singh '}),
            'rating': forms.NumberInput(attrs={'class': 'input-box', 'min': 1, 'max': 5}),
            'review_text': forms.Textarea(attrs={'class': 'input-box', 'rows': 4, 'placeholder': 'Write patient feedback here...'}),
            'is_verified_patient': forms.CheckboxInput(attrs={'class': 'checkbox-box'})
        }

class EarningForm(forms.ModelForm):
    class Meta:
        model = PayoutEarning
        fields = ['patient_name', 'amount', 'status', 'payment_date']
        
        widgets = {
            'patient_name': forms.TextInput(attrs={'class': 'input-box', 'placeholder': 'E.g. Rahul Sharma'}),
            'amount': forms.NumberInput(attrs={'class': 'input-box', 'placeholder': 'Fee in ₹'}),
            'status': forms.Select(attrs={'class': 'input-box'}),
            'payment_date': forms.DateTimeInput(attrs={'class': 'input-box', 'type': 'datetime-local'}),
        }




class CustomUserCreationForm(UserCreationForm):
    # Email field ko required aur placeholder ke sath set kiya
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'E.g. doctor@example.com'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    # Form initialize hote waqt saare defaults ko clean karne ka logic
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            # Har field me 'auth-input' class lagayenge (taaki pill-shape design aa jaye)
            field.widget.attrs['class'] = 'auth-input'
            
            # Ye line Django ke default lambe text aur bullet points ko gayab kar degi
            field.help_text = '' 
            
            # Placeholders set karna
            if field_name == 'username':
                field.widget.attrs['placeholder'] = 'Choose a Username'
            elif field_name == 'password1':
                field.widget.attrs['placeholder'] = 'Create Password'
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = 'Confirm Password'