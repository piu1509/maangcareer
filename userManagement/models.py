from typing import Iterable
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from decimal import Decimal
from django.core.validators import MinValueValidator

import logging

logger = logging.getLogger(__name__)

def validate_phone_number(value):
    if not value.isdigit():
        raise ValidationError("Phone number must contain only digits.")
    if len(value) != 10:
        raise ValidationError("Phone number must be exactly 10 digits long.")

Gender = [
    ('Male','Male'),
    ('Female','Female'),
    ('Others','Others')
]      

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # phone_num = models.CharField('Phone Number',max_length=10,null=True,blank=True, help_text="max length is 10")
    phone_num = models.CharField('Phone Number',max_length=10,null=True,blank=True,validators=[validate_phone_number], help_text="max length is 10")
    gender = models.CharField(max_length=10, choices=Gender, null=True, blank=True)
    joined_date = models.DateField('Joined Date',auto_now_add=True)
    profile_img = models.ImageField(upload_to='profile_picture',null = True , blank=True)
    terms_condition = models.BooleanField(default = False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    def is_otp_valid(self):
        if not self.otp or not self.otp_expiry:
            return False
        return timezone.now() <= self.otp_expiry

    def __str__(self) -> str:return self.user.get_full_name() or self.user.username


class StudentPersonalDetails(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='studentDetail')  
    location = models.CharField(max_length=100, blank=True, null=True)
    university = models.CharField(max_length=100, blank=True, null=True) 
    role = models.CharField(max_length=100, blank=True, null=True) 

    def __str__(self):
        return self.student.user.get_full_name() or self.student.user.username

mode_type = (
    ('online', 'online'),
    ('offline', 'offline'),
)

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    phone_num = models.CharField('Phone Number', max_length=10, help_text="max length is 10")
    gender = models.CharField(max_length=10, choices=Gender, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    present_company = models.CharField(max_length=100, blank=True, null=True)
    resume = models.FileField(upload_to='instructor-reumes', blank=True, null=True)
    photo = models.ImageField(upload_to='intructor-photo', blank=True, null=True)
    terms_condition = models.BooleanField(default = False)
    rules_regulation_count =  models.IntegerField(default=0)
    page_visit_count =  models.IntegerField(default=0)
    joined_date = models.DateField('Joined Date',auto_now_add=True)
    signature = models.FileField(upload_to='instructor-signatures', blank=True, null=True)
    password_raw = models.CharField(max_length=15, null=True, blank=True)
    current_salary = models.DecimalField(max_digits=20,decimal_places=2,validators=[MinValueValidator(Decimal('0.01'))],null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
     
        if self.email:
            self.user.email = self.email

        if self.password_raw:
            self.user.set_password(self.password_raw) 
        self.user.save()
        super().save(*args, **kwargs)    

    def __str__(self) -> str:return self.user.get_full_name() or self.user.username


class Notice(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:return self.title


class NotificationStatus(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null = True , blank = True)
    notice = models.ManyToManyField(Notice)
    def __str__(self) :
        return f"{self.student.user.username}"
    

    
class SalesPerson(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    phone_num = models.CharField('Phone Number',max_length=10, help_text="max length is 10")
    gender = models.CharField(max_length=10, choices=Gender, null=True, blank=True)
    location = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='sales-person-photo', blank=True, null=True)
    otp = models.IntegerField(null=True, blank=True, editable=False)
    password_raw = models.CharField(max_length=15, null=True, blank=True)
    otp_validation_time = models.DateTimeField(null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    branch = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    mode = models.CharField(max_length=25, choices=mode_type, default='offline')
    current_salary = models.DecimalField(max_digits=20,decimal_places=2,validators=[MinValueValidator(Decimal('0.01'))],null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
     
        if self.email:
            self.user.email = self.email

        if self.password_raw:
            self.user.set_password(self.password_raw) 
        self.user.save()
        super().save(*args, **kwargs)

    def __str__(self) -> str:return self.user.get_full_name() or self.user.username


class SubAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    phone_num = models.CharField('Phone Number',max_length=10, help_text="max length is 10")
    gender = models.CharField(max_length=10, choices=Gender, null=True, blank=True)
    location = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='sub-admin-photo', blank=True, null=True)
    otp = models.IntegerField(null=True, blank=True, editable=False)
    password_raw = models.CharField(max_length=15, null=True, blank=True)
    otp_validation_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
     
        if self.email:
            self.user.email = self.email

        if self.password_raw:
            self.user.set_password(self.password_raw) 
        self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

class DataEntryUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    phone_num = models.CharField('Phone Number',max_length=10, help_text="max length is 10")
    gender = models.CharField(max_length=10, choices=Gender, null=True, blank=True)
    location = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='data-entry-user-photo', blank=True, null=True)
    otp = models.IntegerField(null=True, blank=True, editable=False)
    password_raw = models.CharField(max_length=15, null=True, blank=True)
    otp_validation_time = models.DateTimeField(null=True, blank=True)
    current_salary = models.DecimalField(max_digits=20,decimal_places=2,validators=[MinValueValidator(Decimal('0.01'))],null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
     
        if self.email:
            self.user.email = self.email

        if self.password_raw:
            self.user.set_password(self.password_raw) 
        self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

class ExpenseOptions(models.Model):
    type = models.CharField(max_length=255,null=True, blank=True)

    def __str__(self):
        return self.type

USER_TYPE = [
    ('sub_admin', 'Sub Admin'),
    ('mentor', 'Mentor'),
    ('data_entry', 'Data Entry'),
    ('sales', 'Sales'),
]

class Expense(models.Model):
    type = models.ForeignKey(ExpenseOptions, on_delete=models.CASCADE, null=True, blank=True)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='toUser', null=True, blank=True)
    to_user_details = models.CharField(max_length=255, null=True, blank=True)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, name='fromUser')
    to_user_type = models.CharField(max_length=25, choices=USER_TYPE, null=True, blank=True)
    amount = models.DecimalField(max_digits=20,decimal_places=2,validators=[MinValueValidator(Decimal('0.01'))],null=True, blank=True)
    date_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    receipt = models.FileField(upload_to='expense-receipt', null=True, blank=True)
    transaction_no = models.CharField(max_length=255, null=True, blank=True)
    mode = models.CharField(max_length=255, null=True, blank=True)
    status = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.expense_type} - {self.to_user.username}'

STATUS_TYPE = [
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('pending', 'Pending')
]

class LeaveRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leaveuser")
    user_type = models.CharField(max_length=20, choices=USER_TYPE)
    type = models.CharField(max_length=100)
    reason = models.TextField()
    num_of_days = models.IntegerField()
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_TYPE, default="pending")
    status_description = models.TextField(null=True, blank=True)

    
    def __str__(self):
        return f"{self.user.username} - {self.user_type} - {self.status}" 


