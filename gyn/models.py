from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator 
from django.utils import timezone 
from django.conf import settings 
from django.contrib.auth.models import User 

class Appointment(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    booking_id = models.CharField(max_length=20, unique=True, blank=True, null=True) 
    patient_name = models.CharField(max_length=100)
    email = models.EmailField()
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def save(self, *args, **kwargs):
        if not self.booking_id:
            last_appointment = Appointment.objects.all().order_by('id').last()
            if last_appointment:
                next_id = last_appointment.id + 1
            else:
                next_id = 1
            self.booking_id = str(next_id)
        super(Appointment, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id} - {self.patient_name}"


# =======================================================
# REVIEW MODELS (Helpful & Reply Fix)
# =======================================================
class Review(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    # Basic Patient Info
    patient_name = models.CharField(max_length=100)
    is_verified_patient = models.BooleanField(default=True)
    
    # Review Details
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    review_text = models.TextField()
    
    # Tracking & Actions
    created_at = models.DateTimeField(default=timezone.now)
    helpful_count = models.IntegerField(default=0) # Yeh sirf 1 baar likhna hai
    helpful_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    
    # Status for "Pending Replies" KPI card
    REPLY_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Replied', 'Replied'),
    ]
    reply_status = models.CharField(max_length=20, choices=REPLY_STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.patient_name} - {self.rating} Stars"

# NAYA MODEL YAHAN ADD KIYA GAYA HAI
class ReviewReply(models.Model):
    review = models.ForeignKey(Review, related_name='replies', on_delete=models.CASCADE)
    replier_name = models.CharField(max_length=100, default="Admin / Doctor")
    reply_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply to Review ID: {self.review.id}"


# =======================================================
# EARNING MODEL
# =======================================================
class PayoutEarning(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earnings', null=True, blank=True)
    STATUS_CHOICES = [
        ('Completed', 'Completed (Active Earning)'),
        ('Pending', 'Pending (Awaiting Settlement)'),
        ('Withdrawn', 'Withdrawn (Payout Processed)'),
    ]
    patient_name = models.CharField(max_length=100, help_text="Patient ya Client ka naam")
    amount = models.IntegerField(help_text="Consultation Fee (in ₹)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Completed')
    payment_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.patient_name} - ₹{self.amount} ({self.status})"


# =======================================================
# COMMISSION CONFIGURATION
# =======================================================
class PricingConfiguration(models.Model):
    name = models.CharField(max_length=100, default="Standard Pricing")
    is_active = models.BooleanField(default=True)
    
    call_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    call_fee_pct = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    call_tax_pct = models.DecimalField(max_digits=5, decimal_places=2, default=18)

    video_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    video_fee_pct = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    video_tax_pct = models.DecimalField(max_digits=5, decimal_places=2, default=18)

    chat_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    chat_fee_pct = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    chat_tax_pct = models.DecimalField(max_digits=5, decimal_places=2, default=18)

    clinic_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    clinic_fee_pct = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    clinic_tax_pct = models.DecimalField(max_digits=5, decimal_places=2, default=18)

    nurse_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nurse_fee_pct = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    nurse_tax_pct = models.DecimalField(max_digits=5, decimal_places=2, default=18)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# =======================================================
# PATIENT MODEL
# =======================================================
class Patient(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patients', null=True, blank=True)
    STATUS_CHOICES = (
        ('Pregnant', 'Pregnant'),
        ('Postpartum', 'Postpartum'),
        ('Planning', 'Planning'),
        ('Not Pregnant', 'Not Pregnant'),
        ('No Show', 'No Show'),
        ('Drama Queen', 'Drama Queen'), 
    )
    
    RISK_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    )

    patient_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    avatar_emoji = models.CharField(max_length=10, blank=True, null=True, help_text="Jaise 🦇, 🦖, 👻") 
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=15)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Planning')
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, default='Low')
    
    age = models.IntegerField()
    city = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient_id} - {self.name}"


# =======================================================
# SERVICE AREA MODEL
# =======================================================
class ServiceArea(models.Model):
    ZONE_CHOICES = (
        ('ZONE 01', 'Primary Location'),
        ('ZONE 02', 'Secondary Location'),
    )

    zone_type = models.CharField(max_length=20, choices=ZONE_CHOICES, default='ZONE 01')
    area_name = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. COD (Kanpur Nagar)")
    pincode = models.CharField(max_length=6)
    city = models.CharField(max_length=100)
    
    service_radius = models.IntegerField(default=12) 
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.zone_type} - {self.area_name} ({self.pincode})"
        