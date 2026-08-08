from django.shortcuts import render, redirect, get_object_or_404
from .models import Student


def home(request):
    return render(request, 'students/home.html')


def student_list(request):
    students = Student.objects.all()

    return render(
        request,
        'students/student_list.html',
        {'students': students}
    )


def add_student(request):

    if request.method == 'POST':

        Student.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            course=request.POST.get('course'),
            age=request.POST.get('age')
        )

        return redirect('student_list')

    return render(request, 'students/add_student.html')


def edit_student(request, id):

    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':

        student.name = request.POST.get('name')
        student.email = request.POST.get('email')
        student.phone = request.POST.get('phone')
        student.course = request.POST.get('course')
        student.age = request.POST.get('age')

        student.save()

        return redirect('student_list')

    return render(
        request,
        'students/edit_student.html',
        {'student': student}
    )


def delete_student(request, id):

    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        student.delete()

    return redirect('student_list')