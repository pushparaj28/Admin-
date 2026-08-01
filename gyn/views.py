
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
# yaha mene form ko import kiya hai 
from .forms import CustomUserCreationForm
from .models import Appointment, Patient, Review, PayoutEarning
from django.db.models import OuterRef, Subquery, Sum, Count
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages #tost message ke pribuilt libaray 
from django.core.paginator import Paginator #page ke liye perebuilt 
from django.db.models import Q #earch fiter ke liye 

import calendar
from datetime import datetime
from .models import Appointment 
from .forms import AppointmentForm

from .models import Review
from .forms import ReviewForm
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
import json
from .models import Review, ReviewReply

# payout ke liye
from .models import PayoutEarning

from django.db.models import Sum, Avg,Count,Q
from datetime import date #date time model
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate
import json
from .forms import EarningForm

#  chart ke liye review vala 
import json
import calendar
from django.utils import timezone
from django.contrib.auth.models import User

# review le liye hai ye  ---------
from django.shortcuts import render
from django.db.models import Avg
from django.core.paginator import Paginator # type: ignore
from .models import Review

# Commission & Pricing Configuration ka page
from .models import PricingConfiguration
# -----------------------------------------

# <-- Patient model
from .models import Patient
#  setting area ke liye 

from .models import ServiceArea

from django.contrib.auth.decorators import user_passes_test

from django.core.exceptions import PermissionDenied


@user_passes_test(lambda u: u.is_superuser, login_url='login')
def manage_doctors(request):
    doctors = User.objects.all().exclude(username=request.user.username)
    return render(request, 'gyn/manage_doctors.html', {'doctors': doctors})

# // kisi bhi doctor ko super admin bnana ke liye  
@user_passes_test(lambda u: u.is_superuser)
def toggle_admin(request, user_id):
    doctor = get_object_or_404(User, id=user_id)
    
    # Khud ko admin se remove na karein (safety)
    if doctor != request.user:
        # Status toggle karein
        new_status = not doctor.is_superuser
        
        doctor.is_superuser = new_status
        doctor.is_staff = new_status
        
        # Sirf in do fields ko update karein (MySQL ke liye fast)
        doctor.save(update_fields=['is_superuser', 'is_staff'])
        
        print(f"User {doctor.username} is_superuser set to: {new_status}")
        
    return redirect('manage_doctors')

# // global report ke liye 
@user_passes_test(lambda u: u.is_superuser, login_url='login')
def global_report(request):
    if not request.user.is_superuser:
        return redirect('dashboard')

    # 1. Earnings ki subquery (Sirf 'Completed' status wali)
    earnings_sub = PayoutEarning.objects.filter(
        doctor=OuterRef('pk'), 
        status='Completed'
    ).values('doctor').annotate(total=Sum('amount')).values('total')
    
    # 2. Appointments ki subquery
    appt_sub = Appointment.objects.filter(doctor=OuterRef('pk')).values('doctor').annotate(total=Count('id')).values('total')
    
    # 3. Unique Patients ki subquery (Patient name ke basis par)
    patient_sub = Appointment.objects.filter(doctor=OuterRef('pk')).values('doctor').annotate(total=Count('patient_name', distinct=True)).values('total')

    # 4. Final Report
    report = User.objects.filter(is_superuser=False).annotate(
        total_earned=Subquery(earnings_sub),
        total_appointments=Subquery(appt_sub),
        total_patients=Subquery(patient_sub)
    )
    
    return render(request, 'gyn/global_report.html', {'report': report})

# Ek chhota sa check function banaiye
def is_superadmin(user):
    if user.is_superuser:
        return True
    raise PermissionDenied


# // super admin ka login karke ke liye 
@login_required
def impersonate_doctor(request, doctor_id):
    # Sirf superuser hi ye kar sakta hai
    if not request.user.is_superuser:
        return redirect('dashboard')

    doctor = get_object_or_404(User, id=doctor_id)
    
    # Backend mein user ko switch karna
    # 'django.contrib.auth.backends.ModelBackend' zaroori hai
    login(request, doctor, backend='django.contrib.auth.backends.ModelBackend')
    
    return redirect('dashboard') # Ya doctor ka specific dashboard

@login_required(login_url='login')
def appointments_view(request):
    # ==========================================
    # 1. THE MAGIC FILTER (Super Admin vs Doctor)
    # ==========================================
    # Sabse pehle check karo user kaun hai, aur uska 'base data' nikal lo
    if request.user.is_superuser:
        base_query = Appointment.objects.all()
    else:
        base_query = Appointment.objects.filter(doctor=request.user)

    # ==========================================
    # 2. KPI CARDS DATA (Updated)
    # ==========================================
    # Ab 'Appointment.objects' ki jagah 'base_query' ka use karenge
    total_bookings = base_query.count() 
    todays_bookings = base_query.filter(appointment_date=date.today()).count() 
    confirmed_bookings = base_query.filter(status='Confirmed').count() 
    pending_bookings = base_query.filter(status='Pending').count()

    # ==========================================
    # 3. BASE DATA FETCH (Updated)
    # ==========================================
    # Usi filter hue data ko latest date ke hisaab se sort kar lo
    appointments_list = base_query.order_by('-appointment_date', '-id')

    # ==========================================
    # 4. DATE FILTER LOGIC
    # ==========================================
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        appointments_list = appointments_list.filter(appointment_date__range=[start_date, end_date])
    elif start_date:
        appointments_list = appointments_list.filter(appointment_date__gte=start_date)
    elif end_date:
        appointments_list = appointments_list.filter(appointment_date__lte=end_date)

    # ==========================================
    # 5. SEARCH FILTER LOGIC
    # ==========================================
    search_query = request.GET.get('q')   
    if search_query:
        appointments_list = appointments_list.filter(
            Q(booking_id__icontains=search_query) | 
            Q(patient_name__icontains=search_query)
        )

    # ==========================================
    # 6. PAGINATION LOGIC (SABSE AAKHIR ME)
    # ==========================================
    paginator = Paginator(appointments_list, 6) # 1 page par 6 items
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # ==========================================
    # 7. FINAL CONTEXT
    # ==========================================
    context = {
        'appointments': page_obj,  
        'total_bookings': total_bookings,
        'todays_bookings': todays_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
    }
    
    return render(request, 'gyn/appointment.html', context)

# Agar ye import nahi hai toh sabse upar add kar lein

# @login_required yeh ensure karega ki bina login koi is page par na aa paye
@login_required(login_url='login') 
def add_appointment(request):
    if request.method == 'POST':
        # Agar user ne form submit kiya hai (Save button dabaya hai)
        form = AppointmentForm(request.POST)
        if form.is_valid():
            
            # 1. DATABASE ME JAANE SE ROKO (commit=False)
            appointment = form.save(commit=False)
            
            # 2. MAGIC LINE: Login user (doctor) ka data record me daal do
            appointment.doctor = request.user 
            
            # 3. AB FINALLY MYSQL ME SAVE KAR DO
            appointment.save() 
            
            messages.success(request, 'Appointment successfully created!')
            return redirect('appointments') # Save hone ke baad wapas table wale page par bhej do
    else:
        # Agar user sirf page khol raha hai (khali form dikhao)
        form = AppointmentForm()
        
    return render(request, 'gyn/add_appointment.html', {'form': form})


#Edit ke lie function define kiya hai. 
@login_required(login_url='login')
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
@login_required(login_url='login')
def delete_appointment(request, id):
    # 1. Database se us specific appointment ko nikaalo
    appointment = get_object_or_404(Appointment, id=id)
    
    # 2. Usko delete kar do
    appointment.delete()
    messages.warning(request, 'Appointment deleted permanently.')
    # 3. Delete hone ke baad wapas appointments table wale page par bhej do
    return redirect('appointments')

#aane vele pages ke liye banaya gya simple hmtl page. 
# @login_required(login_url='login') 
def coming_soon(request):
    return render(request, 'gyn/coming_soon.html')


   #ye function hai growth insights ka +chart show karana=e ka. 
@login_required(login_url='login') 
@user_passes_test(is_superadmin)
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




    # // earning layout 
@login_required(login_url='login')
def earnings_view(request):
    # 1. Base Query
    if request.user.is_superuser:
        earnings_query = PayoutEarning.objects.all()
    else:
        earnings_query = PayoutEarning.objects.filter(doctor=request.user)

    # 2. Date Filter Logic
    date_filter = request.GET.get('date_filter', 'all')
    now = timezone.now()
    if date_filter == 'this_month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        earnings_query = earnings_query.filter(payment_date__gte=start_date)
    elif date_filter == 'last_month':
        first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        start_date = last_day_last_month.replace(day=1)
        earnings_query = earnings_query.filter(payment_date__gte=start_date, payment_date__lt=first_day_this_month)

    # 3. Dynamic Cards Calculations
    completed_earnings = earnings_query.filter(status='Completed').aggregate(Sum('amount'))['amount__sum'] or 0
    total_withdrawn = earnings_query.filter(status='Withdrawn').aggregate(Sum('amount'))['amount__sum'] or 0
    available_balance = completed_earnings - total_withdrawn
    pending_payments = earnings_query.filter(status='Pending').aggregate(Sum('amount'))['amount__sum'] or 0
    completed_appointments = earnings_query.filter(status='Completed').count()
    avg_fee = int(completed_earnings / completed_appointments) if completed_appointments > 0 else 0

    # 4. Pagination
    paginator = Paginator(earnings_query.order_by('-payment_date'), 5)
    recent_earnings = paginator.get_page(request.GET.get('page'))
    
    # 5. Charts Logic
    daily_earnings = earnings_query.filter(status='Completed') \
                                   .annotate(date=TruncDate('payment_date')) \
                                   .values('date').annotate(total=Sum('amount')).order_by('date')
    
    chart_labels = [item['date'].strftime("%d %b") for item in daily_earnings if item['date']]
    chart_data = [item['total'] or 0 for item in daily_earnings]

    breakdown_aggr = earnings_query.values('status').annotate(total_amount=Sum('amount'))
    breakdown_labels = [item['status'] for item in breakdown_aggr]
    breakdown_data = [item['total_amount'] or 0 for item in breakdown_aggr]
    
    # 6. Final Context
    context = {
        'total_earnings': completed_earnings,
        'available_balance': available_balance,
        'total_withdrawn': total_withdrawn,
        'pending_payments': pending_payments,
        'consultation_count': completed_appointments,
        'average_fee': avg_fee,
        'recent_earnings': recent_earnings,
        'current_filter': date_filter,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'breakdown_labels': json.dumps(breakdown_labels),
        'breakdown_data': json.dumps(breakdown_data),
    }
    return render(request, 'gyn/earnings.html', context)

# 1. ADD Earning
@login_required(login_url='login')
def add_earning(request):
    if request.method == 'POST':
        form = EarningForm(request.POST)
        if form.is_valid():
            
            # 1. DATABASE ME JAANE SE ROKO (commit=False)
            earning = form.save(commit=False)
            
            # 2. MAGIC LINE: Login doctor ka naam daal do
            earning.doctor = request.user 
            
            # 3. AB FINALLY MYSQL ME SAVE KAR DO
            earning.save()
            
            messages.success(request, 'Earning successfully save ho gayi hai!')
            return redirect('earnings')
    else:
        form = EarningForm()
    
    return render(request, 'gyn/earning_form.html', {'form': form, 'title': 'Add New Earning'})


@login_required(login_url='login')
# 2. EDIT Earning
def edit_earning(request, id):
    earning = get_object_or_404(PayoutEarning, id=id)
    if request.method == 'POST':
        form = EarningForm(request.POST, instance=earning)
        if form.is_valid():
            form.save()
            messages.success(request, 'Earning successfully Edit ho gayi hai!')
            return redirect('earnings')
    else:
        form = EarningForm(instance=earning)
        
        
    return render(request, 'gyn/earning_form.html', {'form': form, 'title': 'Edit Earning'})

# 3. DELETE Earning
@login_required(login_url='login')
def delete_earning(request, id):
    earning = get_object_or_404(PayoutEarning, id=id)
    earning.delete()
    messages.success(request, 'Earning  successfully Deleted  ho gayi hai!')
    return redirect('earnings')





@login_required(login_url='login')
def availability_view(request):
    # Abhi ke liye hum dummy data bhej rahe hain layout ke liye.
    # Baad me ise actual database se link karenge.
    context = {
        'weekly_hours': 0,
        'active_days': 4,
        'avg_consult_time': 0,
    }
    return render(request, 'gyn/availability.html', context)



# // review ke liye logic hai 

@login_required(login_url='login')
def reviews_view(request):
    # ==========================================
    # 1. THE MAGIC FILTER (Super Admin vs Doctor)
    # ==========================================
    # System check karega ki kisne login kiya hai
    if request.user.is_superuser:
        base_query = Review.objects.prefetch_related('replies').all()
    else:
        base_query = Review.objects.prefetch_related('replies').filter(doctor=request.user)

    # Base query ko latest ke hisaab se sort kar diya
    reviews_query = base_query.order_by('-created_at')

    # ==========================================
    # 2. URL Parameters (Search & Filter)
    # ==========================================
    search_query = request.GET.get('search', '')
    rating_filter = request.GET.get('rating', 'all')

    # Search Logic
    if search_query:
        reviews_query = reviews_query.filter(
            Q(patient_name__icontains=search_query) | 
            Q(review_text__icontains=search_query)
        )

    # Rating Filter Logic
    if rating_filter != 'all':
        reviews_query = reviews_query.filter(rating=rating_filter)

    # ==========================================
    # 3. CARDS & PERCENTAGE CALCULATION
    # ==========================================
    total_reviews = reviews_query.count()
    
    avg_rating_aggr = reviews_query.aggregate(Avg('rating'))
    average_rating = round(avg_rating_aggr['rating__avg'] or 0, 1)
    
    # Positive Percentage (4 aur 5 star wale)
    positive_reviews = reviews_query.filter(rating__gte=4).count()
    if total_reviews > 0:
        positive_percentage = int((positive_reviews / total_reviews) * 100)
    else:
        positive_percentage = 0
        
    # UPDATE: Ab 'pending_replies' automatic DOCTOR ke base_query se nikal kar aayega!
    pending_replies = base_query.filter(replies__isnull=True).count() 

    # ==========================================
    # 4. RATING DISTRIBUTION (Progress Bars ke liye)
    # ==========================================
    rating_counts = {
        'five': reviews_query.filter(rating=5).count(),
        'four': reviews_query.filter(rating=4).count(),
        'three': reviews_query.filter(rating=3).count(),
        'two': reviews_query.filter(rating=2).count(),
        'one': reviews_query.filter(rating=1).count(),
    }

    # ==========================================
    # 5. CHART DATA
    # ==========================================
    chart_aggr = reviews_query.values('rating').annotate(count=Count('id')).order_by('-rating')
    chart_labels = [f"{item['rating']} Stars" for item in chart_aggr if item['rating']]
    chart_data = [item['count'] for item in chart_aggr if item['rating']]

    # ==========================================
    # 6. PAGINATION
    # ==========================================
    paginator = Paginator(reviews_query, 5)
    page_number = request.GET.get('page')
    paginated_reviews = paginator.get_page(page_number)

    # ==========================================
    # 7. CONTEXT
    # ==========================================
    context = {
        'reviews': paginated_reviews,
        'current_search': search_query,
        'current_rating': rating_filter,
        
        'total_reviews': total_reviews,
        'average_rating': average_rating,
        'positive_percentage': positive_percentage,
        'pending_replies': pending_replies, # Real dynamic data
        
        'rating_counts': rating_counts,
        
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'gyn/reviews.html', context)

# 1. Helpful Count Function
def mark_helpful(request, review_id):
    if request.method == "POST":
        # 1. Check karein ki user login hai ya nahi
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Please login to vote.'})

        review = get_object_or_404(Review, id=review_id)

        # 2. Check karein ki kya is user ne pehle se click kiya hua hai?
        if request.user in review.helpful_users.all():
            # Agar HAAN: Toh user ko remove karo aur count -1 kar do (Unlike)
            review.helpful_users.remove(request.user)
            review.helpful_count -= 1
        else:
            # Agar NAHI: Toh user ko add karo aur count +1 kar do (Like)
            review.helpful_users.add(request.user)
            review.helpful_count += 1

        review.save()
        return JsonResponse({'status': 'success', 'new_count': review.helpful_count})
        
    return JsonResponse({'status': 'error'}, status=400)

# 2. Reply Function
def add_review_reply(request, review_id):
    if request.method == "POST":
        review = get_object_or_404(Review, id=review_id)
        name = request.POST.get('replier_name', 'User')
        text = request.POST.get('reply_text')
        if text:
         ReviewReply.objects.create(review=review, replier_name=name, reply_text=text)
    return redirect(request.META.get('HTTP_REFERER', '/'))

# 4. EDIT & DELETE REPLY LOGIC (Admin Only)
# ========================================================
def delete_review_reply(request, reply_id):
    reply = get_object_or_404(ReviewReply, id=reply_id)
    reply.delete()
    # Delete karke wapas usi page par bhej do
    return redirect(request.META.get('HTTP_REFERER', '/'))


def edit_review_reply(request, reply_id):
    reply = get_object_or_404(ReviewReply, id=reply_id)
    if request.method == "POST":
        new_text = request.POST.get('reply_text')
        if new_text:
            reply.reply_text = new_text
            reply.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))

# 1. CREATE: Naya Review Add Karna
@login_required(login_url='login')
def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            
            # 1. DATABASE ME JAANE SE ROKO (commit=False)
            review = form.save(commit=False)
            
            # 2. MAGIC LINE: Login doctor ka naam daal do
            review.doctor = request.user 
            
            # 3. AB FINALLY MYSQL ME SAVE KAR DO
            review.save()
            
            messages.success(request, 'Review Add ho gaya hai!')
            return redirect('reviews') # Save hone ke baad wapas dashboard par bhej do
    else:
        form = ReviewForm()
    
    context = {'form': form, 'title': 'Add New Review'}
    return render(request, 'gyn/review_form.html', context)

# 2. UPDATE: Purana Review Edit Karna
@login_required(login_url='login')
def edit_review(request, id):
    review = get_object_or_404(Review, id=id) # ID ke hisaab se data nikalo
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review successfully Edit ho gaya hai!')
            return redirect('reviews')
    else:
        form = ReviewForm(instance=review) # Purana data form me bhar do
        
    context = {'form': form, 'title': 'Edit Review'}
    return render(request, 'gyn/review_form.html', context)

# 3. DELETE: Review Delete Karna
@login_required(login_url='login')
def delete_review(request, id):
    review = get_object_or_404(Review, id=id)
    review.delete()
    messages.success(request, 'Review successfully Delete ho gaya hai!')
    return redirect('reviews')


# AUTHENTICATION VIEWS (Login / Signup)
# ==========================================

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please sign in with your credentials.')
            return redirect('login') # Dashboard ki jagah direct LOGIN page par bhej diya
            
    else:
        form = CustomUserCreationForm()
    return render(request, 'gyn/signup.html', {'form': form})

def login_view(request):
    # Agar user pehle se login hai, toh wapas login page na dikhaye
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard') # Sahi password par dashboard par bhej do
    else:
        form = AuthenticationForm()
    return render(request, 'gyn/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login') # Logout hone ke baad wapas login page par


# // Commission & Pricing Configuration ka page ke liye 

@login_required(login_url='login')
def pricing_view(request):
    # Ek active configuration dhundo, nahi hai toh default create kar do
    config, created = PricingConfiguration.objects.get_or_create(
        is_active=True, 
        defaults={'name': 'Default Plan'}
    )

    if request.method == 'POST':
        try:
            # Form se data utha kar save karna (Update)
            config.call_base = request.POST.get('call_base', 0)
            config.call_fee_pct = request.POST.get('call_fee_pct', 12)
            config.call_tax_pct = request.POST.get('call_tax_pct', 18)

            config.video_base = request.POST.get('video_base', 0)
            config.video_fee_pct = request.POST.get('video_fee_pct', 12)
            config.video_tax_pct = request.POST.get('video_tax_pct', 18)

            config.chat_base = request.POST.get('chat_base', 0)
            config.chat_fee_pct = request.POST.get('chat_fee_pct', 12)
            config.chat_tax_pct = request.POST.get('chat_tax_pct', 18)

            config.clinic_base = request.POST.get('clinic_base', 0)
            config.clinic_fee_pct = request.POST.get('clinic_fee_pct', 12)
            config.clinic_tax_pct = request.POST.get('clinic_tax_pct', 18)

            config.nurse_base = request.POST.get('nurse_base', 0)
            config.nurse_fee_pct = request.POST.get('nurse_fee_pct', 12)
            config.nurse_tax_pct = request.POST.get('nurse_tax_pct', 18)

            # Active status toggle via checkbox
            config.is_active = True if request.POST.get('is_active') else False
            config.save()

            messages.success(request, 'Pricing configuration successfully update ho gayi hai!')
            return redirect('pricing') # Apne URL pattern ka naam yahan likhein
            
        except Exception as e:
            messages.error(request, f'Error saving data: {str(e)}')

    context = {'config': config}
    return render(request, 'gyn/pricing.html', context)


# // patients ke liye liye logic 
@login_required(login_url='login')
def patients_dashboard(request):
    
    # ==========================================
    # 1. THE MAGIC FILTER (Super Admin vs Doctor)
    # ==========================================
    if request.user.is_superuser:
        base_query = Patient.objects.all()
    else:
        base_query = Patient.objects.filter(doctor=request.user)

    # Base query se list nikalo aur usko sort karo
    patients = base_query.order_by('-created_at')
    
    # ==========================================
    # 2. Search & Filters uthana
    # ==========================================
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    risk_filter = request.GET.get('risk', 'all')
    
    # ==========================================
    # 3. Filter Logic Apply karna
    # ==========================================
    if search_query:
        patients = patients.filter(
            Q(name__icontains=search_query) | 
            Q(mobile__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(patient_id__icontains=search_query)
        )
        
    if status_filter != 'all':
        patients = patients.filter(status=status_filter)
        
    if risk_filter != 'all':
        patients = patients.filter(risk_level=risk_filter)

    # --- PAGINATION KA LOGIC ---
    paginator = Paginator(patients, 5) # 1 page par 5 patients dikhenge
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ==========================================
    # 4. KPI Cards Calculation (Using base_query)
    # ==========================================
    # Ab cards me kisi aur doctor ke patients count nahi honge!
    total_patients = base_query.count()
    pregnant_count = base_query.filter(status='Pregnant').count()
    postpartum_count = base_query.filter(status='Postpartum').count()
    high_risk_count = base_query.filter(risk_level='High').count()
    missed_count = base_query.filter(status='No Show').count()

    # Percentages nikalna (0 se divide hone ka error rokne ke liye condition)
    pregnant_pct = round((pregnant_count / total_patients * 100), 1) if total_patients > 0 else 0
    postpartum_pct = round((postpartum_count / total_patients * 100), 1) if total_patients > 0 else 0
    high_risk_pct = round((high_risk_count / total_patients * 100), 1) if total_patients > 0 else 0

    # ==========================================
    # 5. CONTEXT
    # ==========================================
    context = {
        'patients': page_obj, # UPDATE: Yahan template me paginated data bhejna zaroori hai
        'search_query': search_query,
        'status_filter': status_filter,
        'risk_filter': risk_filter,
        
        # KPIs Context
        'total_patients': total_patients,
        'pregnant_count': pregnant_count,
        'postpartum_count': postpartum_count,
        'high_risk_count': high_risk_count,
        'missed_count': missed_count,
        
        'pregnant_pct': pregnant_pct,
        'postpartum_pct': postpartum_pct,
        'high_risk_pct': high_risk_pct,
        
        'page_obj': page_obj,  
        'paginator': paginator,
    }
    return render(request, 'gyn/patients_dashboard.html', context)


# Create Operation (Naya Patient Add karne ke liye)
@login_required(login_url='login')
def add_patient(request):
    if request.method == 'POST':
        try:
            # Form se data uthana
            patient_id = request.POST.get('patient_id')
            name = request.POST.get('name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            status = request.POST.get('status')
            risk_level = request.POST.get('risk_level')
            age = request.POST.get('age')
            city = request.POST.get('city')
            avatar_emoji = request.POST.get('avatar_emoji', '👤')
            
            # Database mein create karna
            Patient.objects.create(
                doctor=request.user,  # <--- MAGIC LINE: Ye login wale doctor ko patient se link kar degi
                patient_id=patient_id,
                name=name,
                email=email,
                mobile=mobile,
                status=status,
                risk_level=risk_level,
                age=age,
                city=city,
                avatar_emoji=avatar_emoji
            )
            
            messages.success(request, 'Naya patient successfully add ho gaya hai!')
            return redirect('patients_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error saving data: {str(e)}')
            
    # --- AUTO-GENERATE PATIENT ID LOGIC (GET Request ke liye) ---
    # Database se sabse aakhri patient uthao
    last_patient = Patient.objects.order_by('-id').first()
    
    if last_patient and last_patient.patient_id.startswith('P'):
        try:
            # Agar last ID 'P00124' hai, toh usme se '124' nikalo aur 1 plus karo
            last_num = int(last_patient.patient_id[1:])
            next_id = f"P{last_num + 1:05d}"  # 05d ka matlab hai 5 digits (e.g., P00125)
        except ValueError:
            next_id = "P00001"
    else:
        # Agar database khali hai toh pehli ID ye hogi
        next_id = "P00001"
        
    context = {
        'next_patient_id': next_id
    }
        
    return render(request, 'gyn/add_patient.html', context)
    

# 2. Edit Patient View
def edit_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    
    if request.method == 'POST':
        try:
            patient.patient_id = request.POST.get('patient_id')
            patient.name = request.POST.get('name')
            patient.email = request.POST.get('email')
            patient.mobile = request.POST.get('mobile')
            patient.status = request.POST.get('status')
            patient.risk_level = request.POST.get('risk_level')
            patient.age = request.POST.get('age')
            patient.city = request.POST.get('city')
            patient.avatar_emoji = request.POST.get('avatar_emoji', '👤')
            
            patient.save()
            messages.success(request, 'Patient record successfully update ho gaya hai!')
            return redirect('patients_dashboard')
        except Exception as e:
            messages.error(request, f'Error saving data: {str(e)}')
            
    return render(request, 'gyn/edit_patient.html', {'patient': patient})


# 3. Delete Patient View

def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    patient.delete()
    messages.warning(request, 'Patient record successfully delete kar diya gaya hai.')
    return redirect('patients_dashboard')


# //service setting area ke liye. 

def service_areas_settings(request):
    primary_location = ServiceArea.objects.filter(zone_type='ZONE 01').first()

    if request.method == 'POST':
        try:
            area_name = request.POST.get('area_name')
            pincode = request.POST.get('pincode')
            city = request.POST.get('city')
            service_radius = request.POST.get('service_radius', 12)
            
            # --- NAYA: Map se aayi Lat/Lng uthana ---
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            if primary_location:
                primary_location.area_name = area_name
                primary_location.pincode = pincode
                primary_location.city = city
                primary_location.service_radius = service_radius
                
                # --- NAYA: DB mein save karna ---
                if latitude and longitude:
                    primary_location.latitude = latitude
                    primary_location.longitude = longitude
                    
                primary_location.save()
                messages.success(request, 'Primary location update ho gayi hai!')
            else:
                ServiceArea.objects.create(
                    zone_type='ZONE 01',
                    area_name=area_name,
                    pincode=pincode,
                    city=city,
                    service_radius=service_radius,
                    latitude=latitude,   # --- NAYA ---
                    longitude=longitude  # --- NAYA ---
                )
                messages.success(request, 'Nayi primary location save ho gayi hai!')
            
            return redirect('service_areas_settings')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    context = {'primary_location': primary_location}
    return render(request, 'gyn/settings_service_area.html', context)

@login_required(login_url='login')
def dashboard_view(request):
    # ==========================================
    # DATE FILTER LOGIC
    # ==========================================
    current_date = timezone.now().date()
    
    date_str = request.GET.get('date')
    if date_str:
        try:
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
            
    selected_date = current_date.strftime('%Y-%m-%d')

    # ==========================================
    # THE MAGIC FILTER (Super Admin vs Doctor)
    # ==========================================
    if request.user.is_superuser:
        base_appointments = Appointment.objects.all()
        base_patients = Patient.objects.all()
        base_reviews = Review.objects.all()
        base_earnings = PayoutEarning.objects.all()
    else:
        base_appointments = Appointment.objects.filter(doctor=request.user)
        base_patients = Patient.objects.filter(doctor=request.user)
        base_reviews = Review.objects.filter(doctor=request.user)
        base_earnings = PayoutEarning.objects.filter(doctor=request.user)

    # ==========================================
    # 1. TOP KPI CARDS DATA (Using Base Data)
    # ==========================================
    total_appointments = base_appointments.count()
    today_appointments = base_appointments.filter(appointment_date=current_date).count()
    total_patients = base_patients.count()
    total_reviews = base_reviews.count()
    
    earnings_aggr = base_earnings.filter(status='Completed').aggregate(Sum('amount'))
    total_earnings = earnings_aggr['amount__sum'] or 0

    # ==========================================
    # 2. MIDDLE ROW: UPCOMING APPOINTMENTS
    # ==========================================
    upcoming_appointments = base_appointments.filter(
        appointment_date__gte=current_date
    ).order_by('appointment_date', 'appointment_time')[:5]

    # ==========================================
    # 3. MIDDLE ROW: APPOINTMENT STATUS (DONUT)
    # ==========================================
    confirmed_count = base_appointments.filter(status='Confirmed').count()
    completed_count = base_appointments.filter(status='Completed').count()
    cancelled_count = base_appointments.filter(status='Cancelled').count()
    pending_count = base_appointments.filter(status='Pending').count() 

    if total_appointments > 0:
        conf_pct = round((confirmed_count / total_appointments) * 100, 1)
        comp_pct = round((completed_count / total_appointments) * 100, 1)
        canc_pct = round((cancelled_count / total_appointments) * 100, 1)
        pend_pct = round((pending_count / total_appointments) * 100, 1)
    else:
        conf_pct = comp_pct = canc_pct = pend_pct = 0

    # ==========================================
    # 4. BOTTOM ROW: PATIENT DEMOGRAPHICS (DONUT)
    # ==========================================
    age_18_25 = base_patients.filter(age__gte=18, age__lte=25).count()
    age_26_35 = base_patients.filter(age__gte=26, age__lte=35).count()
    age_36_45 = base_patients.filter(age__gte=36, age__lte=45).count()
    age_46_plus = base_patients.filter(age__gte=46).count()
    
    total_demo = age_18_25 + age_26_35 + age_36_45 + age_46_plus
    if total_demo > 0:
        pct_18_25 = round((age_18_25 / total_demo) * 100)
        pct_26_35 = round((age_26_35 / total_demo) * 100)
        pct_36_45 = round((age_36_45 / total_demo) * 100)
        pct_46_plus = round((age_46_plus / total_demo) * 100)
    else:
        pct_18_25 = pct_26_35 = pct_36_45 = pct_46_plus = 0

    # ==========================================
    # 5. BOTTOM ROW: RECENT REVIEWS
    # ==========================================
    recent_reviews = base_reviews.order_by('-created_at')[:3]

    # ==========================================
    # 6. CHARTS DATA (Dummy arrays for UI)
    # ==========================================
    line_labels = ['1 Jul', '5 Jul', '10 Jul', '15 Jul', '20 Jul', '25 Jul', '31 Jul']
    line_appointments = [10, 25, 40, 65, 50, 95, 70]
    line_completed = [5, 12, 22, 18, 25, 50, 38]
    
    bar_labels = ['1 Jul', '7 Jul', '14 Jul', '21 Jul', '28 Jul']
    bar_earnings = [15000, 22000, 18000, 25000, 21000]

    context = {
        'selected_date': selected_date, # Date picker ke liye HTML me bheja
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'total_patients': total_patients,
        'total_reviews': total_reviews,
        'total_earnings': total_earnings,
        
        'upcoming_appointments': upcoming_appointments,
        'recent_reviews': recent_reviews,
        
        'confirmed_count': confirmed_count, 'conf_pct': conf_pct,
        'completed_count': completed_count, 'comp_pct': comp_pct,
        'cancelled_count': cancelled_count, 'canc_pct': canc_pct,
        'pending_count': pending_count, 'pend_pct': pend_pct,
        
        'age_18_25': age_18_25, 'pct_18_25': pct_18_25,
        'age_26_35': age_26_35, 'pct_26_35': pct_26_35,
        'age_36_45': age_36_45, 'pct_36_45': pct_36_45,
        'age_46_plus': age_46_plus, 'pct_46_plus': pct_46_plus,
        
        'line_labels': json.dumps(line_labels),
        'line_appointments': json.dumps(line_appointments),
        'line_completed': json.dumps(line_completed),
        'bar_labels': json.dumps(bar_labels),
        'bar_earnings': json.dumps(bar_earnings),
    }
    
    return render(request, 'gyn/dashboard.html', context)




@user_passes_test(lambda u: u.is_superuser)
def manage_doctors(request):
    doctors = User.objects.filter(is_superuser=False)
    return render(request, 'gyn/manage_doctors.html', {'doctors': doctors})

def delete_doctor(request, user_id):
    User.objects.get(id=user_id).delete() # CASCADE delete apne aap sab uda dega
    return redirect('manage_doctors')

