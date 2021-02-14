from .models import *
from .forms import *
from django.shortcuts import render,redirect,reverse
from django.http import HttpResponseRedirect,HttpResponse
from django.conf import settings
import sendgrid
from sendgrid.helpers.mail import *

# from django.core.mail import S
import json
import datetime

def check_student(func):
    def inner(request,*args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.user_type == 'Student':
                request.session['ADMIN_MAIL'] = settings.ADMIN_MAIL
                return func(request,*args, **kwargs)
        return HttpResponse('NOT AUTHORIZED')
    return inner


@check_student
def student_home(request):
    form = StudentChange(instance=request.user)
    if request.method == 'POST':
        form = StudentChange(request.POST,request.FILES,instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('student_home'))
    return render(request,"students/student_profile.html",{'form':form})


@check_student
def student_teams(request):
    return render(request,"students/student_team.html",{'team':request.user.students.team_set.all()})


@check_student
def student_complaint(request):
    if request.method == 'POST':
        name = request.POST['name']
        complain = request.POST['complain']
        team = request.POST['team']

        sg = sendgrid.SendGridAPIClient(api_key='')
        data = {
            "personalizations": [
                {
                "to": [{'email':settings.ADMIN_MAIL}],
                "subject": f'Complain from: {name}( {request.user.username} ) and team: {team}'
                }
            ],
            "from": {
                "email": settings.FROM_EMAIL
            },
            "content": [
                {
                "type": "text/plain",
                "value": complain
                }
            ]
            }
        response = sg.client.mail.send.post(request_body=data)
        return redirect('complain')

    return render(request,"students/student_complaint.html")

@check_student
def students_form(request):
    return render(request,"students/student_form.html")

@check_student
def get_form(request,pk):
    form = Form.objects.get(pk=pk)
    if form.expiry_date < datetime.datetime.now(form.expiry_date.tzinfo):
        return HttpResponse("CANNOT SUBMIT RESPONSE")
    if not form.is_open:
        return HttpResponse("Form not open for responses")

    if request.user.user_type == 'Student':
        submited_responses = form.submited_responses

        if request.method == 'POST':

            response = json.loads(request.POST['data'])
            for i in form.team.students.all():
                for ques in form.form.keys():
                    submited_responses[i.admin.username][request.user.username][ques] = int(response[i.admin.username][ques])
            form.submited_responses = submited_responses
            form.save()

            print(form.submited_responses)
        questions = list(form.form.keys())

        return render(request,"students/submit_res.html",{"form":form,"questions":questions,"pk":pk})
