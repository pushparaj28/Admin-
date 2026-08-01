from django.urls import path
from . import views
from .views import impersonate_doctor

urlpatterns = [


   path('dashboard/', views.dashboard_view, name='dashboard'),
    # Ab default page ('') login hoga
    path('', views.login_view, name='login'), 
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    # path('dashboard/', views.dashboard_view, name='dashboard'),


    # Ya fir specifically /appointments/ URL ke liye:
    path('appointments/', views.appointments_view, name='appointments'),
    path('add-appointment/', views.add_appointment, name='add_appointment'),
    path('edit-appointment/<int:id>/', views.edit_appointment, name='edit_appointment'),
    #Delete ke liye. hai ye url
    path('delete-appointment/<int:id>/', views.delete_appointment, name='delete_appointment'), 
 
     # urls.py me
    path('growth-insights/', views.growth_insights, name='growth_insights'),

    path('availability/', views.availability_view, name='availability'),
    
    
    path('reviews/', views.reviews_view, name='reviews'),
    path('add-review/', views.add_review, name='add_review'),
    path('edit-review/<int:id>/', views.edit_review, name='edit_review'),
    path('delete-review/<int:id>/', views.delete_review, name='delete_review'),
    path('review/helpful/<int:review_id>/', views.mark_helpful, name='mark_helpful'),
    path('review/reply/<int:review_id>/', views.add_review_reply, name='add_review_reply'),
    path('reply/edit/<int:reply_id>/', views.edit_review_reply, name='edit_review_reply'),
    path('reply/delete/<int:reply_id>/', views.delete_review_reply, name='delete_review_reply'),

    path('earnings/', views.earnings_view, name='earnings'),
    path('add-earning/', views.add_earning, name='add_earning'),
    path('edit-earning/<int:id>/', views.edit_earning, name='edit_earning'),
    path('delete-earning/<int:id>/', views.delete_earning, name='delete_earning'),
    # commision  url 
    path('commission/', views.pricing_view, name='pricing'),
    
    path('withdrawal/', views.earnings_view, name='earnings'),

    path('patients/', views.patients_dashboard, name='patients_dashboard'),
    path('add-patient/', views.add_patient, name='add_patient'),
    path('edit-patient/<int:id>/', views.edit_patient, name='edit_patient'),
    path('delete-patient/<int:id>/', views.delete_patient, name='delete_patient'),
  
   path('settings/', views.service_areas_settings, name='service_areas_settings'),




   # ... baki purane paths ...
    path('manage-doctors/', views.manage_doctors, name='manage_doctors'),
    path('delete-doctor/<int:user_id>/', views.delete_doctor, name='delete_doctor'),
    path('global-report/', views.global_report, name='global_report'),

    path('impersonate/<int:doctor_id>/', impersonate_doctor, name='impersonate_doctor'),
    path('toggle-admin/<int:user_id>/', views.toggle_admin_status, name='toggle_admin'),
    
]
  