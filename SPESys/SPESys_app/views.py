import datetime
from urllib import request

from django.contrib import messages, auth
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render,reverse
from .EmailBackEnd import EmailBackEnd
from .forms import *


def ShowLoginPage(request):
    return render(request,"login_page.html")

def get_profile(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = AdminChange(request.POST,request.FILES,instance=request.user)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/admin_home')
            else:
                render(request,"profile.html",{'form':form})

        return render(request,"profile.html",{'form':AdminChange(instance=request.user)})

    return render(request, "profile.html")

#POST method for login
def doLogin(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user=EmailBackEnd.authenticate(request, username=request.POST.get("email"), password=request.POST.get("password"))
        if user:
            login(request,user)
            if user.user_type == 'Student':
                return HttpResponseRedirect(reverse('students_form'))
            return HttpResponseRedirect('/admin_home')
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect("/")

#Returns usertype
def get_user_details(request):
    if request.user!=None:
        return HttpResponse("User: "+request.user.email+" usertype : " +str(request.user.user_type))
    else:
        return HttpResponse("Please Login")

def logout_user(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
