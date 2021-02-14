from . import students
from django.urls import path

urlpatterns = [
    path('student_teams/',students.student_teams,name='student_teams'),
    path('student_home/',students.student_home,name='student_home'),
    path('get_form/<pk>/',students.get_form,name='get_form'),
    path('students_form/',students.students_form,name='students_form'),
    path('student_complaint/',students.student_complaint,name='complain')
]
