"""SPESys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path,include
from SPESys_app import views, UC_Views
from SPESys import settings
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('',views.ShowLoginPage,name='login'),
    path('doLogin', views.doLogin),
    path('get_profile/', views.get_profile),
    path('get_user_details', views.get_user_details),
    path('logout_user', views.logout_user),
    path('admin_home', UC_Views.admin_home),
    path('add_students', UC_Views.add_students),
    path('add_students_save',UC_Views.add_students_save),
    path('add_team',UC_Views.add_team),
    path('team_autocomplete/',UC_Views.TeamAutocompletesView.as_view()),
    path('student_autocomplete/',UC_Views.StudentAutocompletesView.as_view()),
    path('add_form/',UC_Views.add_form),
    path('create_form/<pk>',UC_Views.create_form,name="create_form"),
    path('see_responses/<pk>/',UC_Views.see_responses,name='see_responses'),

    path('delete_team/<pk>/',UC_Views.delete_team,name='delete_team'),
    path('edit_team/<pk>/',UC_Views.edit_team,name='edit_team'),
    path('delete_form/<pk>/',UC_Views.delete_form,name='delete_form'),
    path('add_csv/',UC_Views.add_csv,name='add_csv'),
    path('view_response/',UC_Views.student_feedback,name='view_response'),
    path('mail_responses/<pk>/',UC_Views.mail_responses,name='mail_responses'),

    path('',include('SPESys_app.urls')),

    path("password_reset/",auth_views.PasswordResetView.as_view(template_name="password_templates/password_reset.html"),name="password_reset"),
    path("password_reset/done/",auth_views.PasswordResetDoneView.as_view(template_name="password_templates/password_reset_done.html"),name="password_reset_done"),
    path("password_reset_confirm/<uidb64>/<token>/",auth_views.PasswordResetConfirmView.as_view(template_name="password_templates/password_reset_confirm.html"),name="password_reset_confirm"),
    path("password_reset_complete",auth_views.PasswordResetCompleteView.as_view(template_name="password_templates/password_reset_complete.html"),name="password_reset_complete"),
    path("password_change",auth_views.PasswordChangeView.as_view(template_name="password_templates/password_change_form.html"),name="password_change"),
    path("password_change_done",auth_views.PasswordChangeDoneView.as_view(template_name="password_templates/password_change_done.html"),name="password_change_done"),


    ]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
