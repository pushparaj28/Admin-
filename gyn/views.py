
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages #tost message ke pribuilt libaray 
from django.core.paginator import Paginator #page ke liye perebuilt 
from django.db.models import Q #earch fiter ke liye 
from datetime import date #date time model
import calendar
from datetime import datetime
from .models import Appointment 
from .forms import AppointmentForm # Agar model ka naam kuch aur hai to change kar lena


#pagination ka code hai ye 
def appointments_view(request):

    total_bookings = Appointment.objects.count() 
    # Sirf aaj ki date wale records count karega
    todays_bookings = Appointment.objects.filter(appointment_date=date.today()).count() 
    # Sirf 'Confirmed' status wale records
    confirmed_bookings = Appointment.objects.filter(status='Confirmed').count() 
    # Sirf 'Pending' status wale records
    pending_bookings = Appointment.objects.filter(status='Pending').count()

    appointment_list = Appointment.objects.all().order_by('-id')
    search_query = request.GET.get('q')   
    if search_query:
        # Agar user ne kuch search kiya hai, to database me filter chalao
        # __icontains ka matlab hai ki exact match nahi chahiye, agar naam ka chhota hissa bhi mile to chalega (case-insensitive)
        appointment_list = appointment_list.filter(
            Q(booking_id__icontains=search_query) | 
            Q(patient_name__icontains=search_query)
        )
    paginator = Paginator(appointment_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'appointments': page_obj,
        'total_bookings': total_bookings,
        'todays_bookings': todays_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
    }
    return render(request, 'gyn/appointment.html', context)



#Add appointment
def add_appointment(request):
    if request.method == 'POST':
        # Agar user ne form submit kiya hai (Save button dabaya hai)
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save() # Data MySQL me save ho jayega
            messages.success(request, 'Appointment successfully created!')
            return redirect('appointments') # Save hone ke baad wapas table wale page par bhej do
    else:
        # Agar user sirf page khol raha hai (khali form dikhao)
        form = AppointmentForm()
    return render(request, 'gyn/add_appointment.html', {'form': form})



#Edit ke lie function define kiya hai. 
def edit_appointment(request, id):
    # 1. Database se wo specific appointment nikaalo
    appointment = get_object_or_404(Appointment, id=id)
    
    if request.method == 'POST':
        # 2. Form me naya data daalo, aur batao ki purana 'instance' kya tha taaki wo update ho, naya create na ho
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointments')
    else:
        # 3. Form ko purane data ke sath pre-fill karke dikhao
        form = AppointmentForm(instance=appointment)
        
    # Hum wahi purana add_appointment.html use kar rahe hain!
    return render(request, 'gyn/add_appointment.html', {'form': form, 'is_edit': True})


#Delate ke liye function : 
def delete_appointment(request, id):
    # 1. Database se us specific appointment ko nikaalo
    appointment = get_object_or_404(Appointment, id=id)
    
    # 2. Usko delete kar do
    appointment.delete()
    messages.warning(request, 'Appointment deleted permanently.')
    # 3. Delete hone ke baad wapas appointments table wale page par bhej do
    return redirect('appointments')

#aane vele pages ke liye banaya gya simple hmtl page.  
def coming_soon(request):
    return render(request, 'gyn/coming_soon.html')


   #ye function hai growth insights ka +chart show karana=e ka.  
def growth_insights(request):
    # --- 1. KPI Cards Ka Purana Logic ---
    total_appointments = Appointment.objects.count()
    completed_count = Appointment.objects.filter(status='Confirmed').count() 
    pending_count = Appointment.objects.filter(status='Pending').count()
    cancelled_count = Appointment.objects.filter(status='Cancelled').count()

    cancellation_rate = 0
    if total_appointments > 0:
        cancellation_rate = round((cancelled_count / total_appointments) * 100, 1)

    status_data = [completed_count, pending_count, cancelled_count]

    # --- 2. LINE CHART KA NAYA LOGIC (Pichle 6 Mahine) ---
    today = datetime.today()
    trend_labels = []
    trend_data = []

    for i in range(5, -1, -1): # Pichle 6 mahine calculate karne ke liye loop
        m = today.month - i
        y = today.year
        if m <= 0:
            m += 12
            y -= 1
        
        # Mahine ka naam nikalna (jaise: Jan, Feb)
        month_name = f"{calendar.month_abbr[m]} {y}" 
        trend_labels.append(month_name)
        
        # Us mahine me kitni appointment aayi, wo count karna
        count = Appointment.objects.filter(appointment_date__year=y, appointment_date__month=m).count()
        trend_data.append(count)

    # --- 3. Context me Data Bhejna ---
    context = {
        'total_appointments': total_appointments,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'cancellation_rate': cancellation_rate,
        'status_data': status_data,
        
        'trend_labels': trend_labels, # Naya data
        'trend_data': trend_data,     # Naya data
    }
    
    return render(request, 'gyn/growth_insights.html', context)