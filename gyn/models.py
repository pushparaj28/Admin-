from django.db import models

class Appointment(models.Model):
    # Status ke options define kar rahe hain
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    # Database Columns (Fields)
    booking_id = models.CharField(max_length=20, unique=True)
    patient_name = models.CharField(max_length=100)
    email = models.EmailField()
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.booking_id} - {self.patient_name}"