from django.urls import path
from . import views

urlpatterns = [
    # Website khulte hi direct Appointment page show karne ke liye:
    path('', views.appointments_view, name='home'),
    
    # Ya fir specifically /appointments/ URL ke liye:
    path('appointments/', views.appointments_view, name='appointments'),
   
    path('add-appointment/', views.add_appointment, name='add_appointment'),
    
    # Ye EDIT wala URL Hai.
    path('edit-appointment/<int:id>/', views.edit_appointment, name='edit_appointment'),

    #Delete ke liye. hai ye url
    path('delete-appointment/<int:id>/', views.delete_appointment, name='delete_appointment'), 



    path('dashboard/', views.coming_soon, name='dashboard'),
    path('patients/', views.coming_soon, name='patients'),
    path('earnings/', views.coming_soon, name='earnings'),
    path('withdrawal/', views.coming_soon, name='withdrawal'),
    path('commission/', views.coming_soon, name='commission'),
    path('reviews/', views.coming_soon, name='reviews'),
    path('availability/', views.coming_soon, name='availability'),
    path('settings/', views.coming_soon, name='settings'),
]
