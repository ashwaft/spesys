from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,reverse
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone,dateparse
from django.core.files.storage import FileSystemStorage,File
from django.conf import settings
from django.core.mail import send_mail,EmailMessage

import json
from .forms import *
from .models import *
from dal import autocomplete
import pandas as pd

def check_lecturer(func):
    def inner(request,*args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.user_type == 'Lecturer':
                return func(request,*args, **kwargs)
        return HttpResponse('NOT AUTHORIZED')
    return inner

class TeamAutocompletesView(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Team.objects.all().order_by('team_id')
        if self.q:
            qs = qs.filter(team_id__istartswith=self.q)
        return qs

class StudentAutocompletesView(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Students.objects.all().order_by('given_name')
        if self.q:
            qs = qs.filter(given_name__istartswith=self.q)
        return qs

@check_lecturer
def admin_home(request):
    if request.user.is_superuser:
        return render(request,"UC/home_content.html")

@check_lecturer
def add_students(request):
    return render(request, "UC/add_students_template.html")

@check_lecturer
def add_csv(request):
    if request.user.is_authenticated:
        file = request.FILES['csv_file']
        fs = FileSystemStorage(location=settings.MEDIA_ROOT+"/csv")
        csv_file = fs.save(file.name,file)
        csv_ = pd.read_csv(settings.MEDIA_ROOT+'/csv/'+csv_file)
        for i,row in csv_.iterrows():
            print(row)
            try:
                user = CustomUser.objects.get(username=row['email'])

            except ObjectDoesNotExist:
                user = CustomUser.objects.create_user(password=row['password'],username=row['email'],user_type = "Student")
                user.save()
            try:
                student = Students.objects.get(id=row['studentid'],admin=user)

            except Students.DoesNotExist:
                student = Students(id=row['studentid'],given_name=row['given name'],surname = row['surname'],title = row['title'],admin=user,teach_period=row['teach period'])
                student.save()

            try:
                team = Team.objects.get(team_id=row['Team number'])
                team.students.add(student)
            except ObjectDoesNotExist:
                team = Team(team_id=row['Team number'],created_by=request.user)
                team.save()
                team.students.add(student)

            team.save()

        return HttpResponseRedirect("/add_students")



@check_lecturer
def add_students_save(request):
    if request.method!="POST":
        return HttpResponse("Error - Please resubmit form")
    else:
        student_id = request.POST.get("student_id")
        given_name = request.POST.get("given_name")
        teach_period = request.POST.get("teach_period")
        surname = request.POST.get("surname")
        title = request.POST.get("title")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        print(password,password2)
        if password != password2:
            messages.error(request,"Passwords didn't match")
            return HttpResponseRedirect("/add_students")

        user = CustomUser.objects.create_user(password=password,username=email,user_type = "Student")
        user.save()

        student = Students(id=student_id,given_name=given_name,admin=user,teach_period=teach_period,surname = surname,title = title)
        student.save()
        messages.success(request, "Sucessfully Added Student(s)")
        return HttpResponseRedirect("/add_students")

@check_lecturer
def add_team(request):
    form = TeamForm()
    if request.method == "POST":
        form = TeamForm(request.POST)

        if form.is_valid():
            ins = form.save()
            ins.created_by = request.user
            ins.save()

            messages.success(request, "Sucessfully created team " + ins.team_id)
            return HttpResponseRedirect("/add_team")

        print(form.errors)
        return render(request, "UC/add_team_template.html",{"form":form})

    return render(request, "UC/add_team_template.html",{"form":form})


@check_lecturer
def edit_team(request,pk):
    obj = Team.objects.get(pk=pk)
    form = TeamForm(instance=obj)
    if request.method == "POST":
        form = TeamForm(instance=obj,data=request.POST)

        if form.is_valid():
            ins = form.save()

            messages.success(request, "Sucessfully edited team " + ins.team_id)
            return HttpResponseRedirect("/add_team")

        print(form.errors)
        return render(request, "UC/edit_team.html",{"form":form})

    return render(request, "UC/edit_team.html",{"form":form})


@check_lecturer
def add_form(request):
    if request.method == 'POST':
        exp = dt.strptime(request.POST['expiry_date'],'%Y-%m-%d %H:%M %z')
        form = Form(form={},team=Team.objects.get(team_id=request.POST['team_id']),submited_responses={},expiry_date=timezone.localtime(exp))
        form.created_by=request.user
        print(type(request.user))
        form.save()
        return HttpResponseRedirect(reverse('create_form',args=(form.pk,)))

    teams = Team.objects.all().values_list("team_id",flat=True)
    return render(request, "UC/add_form.html",{"teams":list(teams)})


@check_lecturer
def create_form(request,pk):
    form = Form.objects.get(pk=pk)
    if request.method == 'POST':

        data = json.loads(request.POST['data'])
        questions = data["questions"]
        # is_edited = True if data['edited'] == 'True' else False
        quest_ = {}
        for i in questions:
            quest_[i] = {'1':0,'2':0,'3':0,'4':0,'5':0}

        form.form = quest_
        submited_responses = {}

        for i in form.team.students.all():
            submited_responses[i.admin.username] = {}
            for j in form.team.students.all():
                submited_responses[i.admin.username][j.admin.username] = {ques:None for ques in questions}

        form.submited_responses = submited_responses
        if request.POST['is_open'] == 'true':
            form.is_open = True
        else:
            form.is_open = False
        form.form_name = request.POST['name']
        form.save()

    return render(request, "UC/create_form.html",{"team":form.team,"form":form,"pk":pk})


@check_lecturer
def student_feedback(request):
    return render(request,'UC/view_response.html',{'form':Form.objects.all()})


@check_lecturer
def see_responses(request,pk):
    form = Form.objects.get(pk=pk)
    for_csv = form.get_average_responses()

    df = pd.DataFrame(for_csv)
    # df.iloc['   '] = 'Average responses'
    print(for_csv)

    return HttpResponse(df.to_html())

@check_lecturer
def mail_responses(request,pk):
    form = Form.objects.get(pk=pk)
    students = list(form.team.students.all().values_list('admin__username',flat=True))
    f_name = f'{settings.MEDIA_ROOT}/csv/response_{dt.now().timestamp()}.csv'
    file = pd.DataFrame(form.get_average_responses())
    file.to_csv(f_name)

    # email = EmailMessage('SPEsys - Response Forms','Hi, You have response awaiting you. Do download CSV attached.',settings.FROM_EMAIL,students)
    email = EmailMessage(settings.EMAIL_SUBJECT_RESPONSE,settings.EMAIL_BODY_RESPONSE,settings.FROM_EMAIL,[settings.ADMIN_MAIL])

    email.attach(filename="response.csv",content=open(f_name).read())
    email.send()
    return HttpResponseRedirect('/view_response')


@check_lecturer
def delete_team(request,pk):
    if request.user.is_authenticated:
        Team.objects.get(pk=pk).delete()
    return HttpResponseRedirect('/add_team')

@check_lecturer
def delete_form(request,pk):
    if request.user.is_authenticated:
        Form.objects.get(pk=pk).delete()
    return HttpResponseRedirect('/add_form')
