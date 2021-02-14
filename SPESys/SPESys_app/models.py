from django.contrib.auth.models import AbstractBaseUser,AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model, base_user
import jsonfield
from statistics import mean
import statistics

def get_team_id():
    id = get_random_string(length=6)
    return "T-"+str(id)

def get_form_id():
    id = get_random_string(length=6)
    return "F-"+str(id)

# Create your models here.
class Manager(BaseUserManager):
    def create_user(self,username,password,**extra_fields):
        if not username:
            raise ValueError(_('The Email must be set'))
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self,username,password,**extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractUser):
    username = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100,default="")
    user_type_data=((1,"Lecturer"),(2,"Student"))
    user_type=models.CharField(choices=user_type_data,max_length=10)
    avatar = models.ImageField(upload_to='images/',null=True,blank=True)

    objects = Manager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['full_name']

    def get_url(self):
        try:
            return self.avatar.url
        except ValueError:
            return '/static/dist/img/defaultUser.png'

class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class Staffs(models.Model):
    id=models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    address=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class Courses(models.Model):
    id=models.AutoField(primary_key=True)
    course_name=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Subjects(models.Model):
    id=models.AutoField(primary_key=True)
    subject_name=models.CharField(max_length=255)
    unit_code_id=models.ForeignKey(Courses,on_delete=models.CASCADE)
    staff_id=models.ForeignKey(Staffs,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Students(models.Model):
    id = models.CharField(max_length=20,unique=True,primary_key=True)
    admin = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    profile_pic = models.FileField()
    given_name=models.TextField(default=None)
    teach_period = models.TextField(default=None)
    surname = models.TextField(default=None)
    title = models.TextField(default=None)
    session_start_year=models.DateField(auto_now_add=True)
    session_end_year=models.DateField(auto_now_add=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.given_name)

class Team(models.Model):
    team_id = models.CharField(max_length=20,unique=True,default=get_team_id)
    students = models.ManyToManyField(Students)
    created_by = models.ForeignKey(to=get_user_model(),on_delete=models.CASCADE,null=True,blank=True)
    def __str__(self):
        return str(self.team_id)

class Form(models.Model):
    form = jsonfield.JSONField()
    team = models.ForeignKey(to=Team,on_delete=models.CASCADE)
    submited_responses = jsonfield.JSONField(default={})
    created_by = models.ForeignKey(to=get_user_model(),on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    form_id = models.CharField(default=get_form_id,max_length=10,unique=True)
    is_open = models.BooleanField(default=False)

    form_name = models.TextField(blank=True,null=True,default='Form')

    def get_average_responses(self):
        res = {}
        num = 0
        for i,j in self.submited_responses.items():
            res[i] = {}
            for sco in list(j.values()):
                for ques in sco.keys():
                    if ques in res[i]: res[i][ques].append(sco[ques])

                    else: res[i][ques]=[sco[ques]]
        for i in res.keys():
            total = 0
            for j in res[i].keys():
                try:
                    avg = mean(list(filter(None,res[i][j])))
                    total += avg
                    res[i][j] = avg
                except statistics.StatisticsError:
                    avg = 'N/A'
                    res[i][j] = avg
            res[i]['Total'] = f'{total}/{len(res[i].keys())*5}'
        return res

class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=255)
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class FeedBackStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=255)
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class NotificationStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

from . import tasks
from datetime import datetime as dt
import datetime

@receiver(post_save,sender=Form)
def init_form(sender,instance,created,**kwargs):
    if created:
        # This will be 7 days before expiry or creation date whichever is maximum.
        eta = max(instance.created_on,instance.expiry_date - datetime.timedelta(days=7))
         # This send emails to students at time calculated in previous step.
        tasks.send_mails.apply_async(args=(instance.pk,),eta=eta)

@receiver(post_delete,sender=Students)
def delete_user(sender,instance,**kwargs):
    try:
        instance.admin.delete()
    except:
        pass
