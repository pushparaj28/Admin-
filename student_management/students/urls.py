from django.urls import path
from django.shortcuts import redirect
from . import views


urlpatterns = [

    # Website open → Students page
    path('', lambda request: redirect('student_list'), name='home'),

    path('students/', views.student_list, name='student_list'),

    path('students/add/', views.add_student, name='add_student'),

    path('students/edit/<int:id>/', views.edit_student, name='edit_student'),

    path('students/delete/<int:id>/', views.delete_student, name='delete_student'),
]