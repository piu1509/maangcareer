from django.db import models
from datetime import timedelta

from django.core.exceptions import ValidationError
from userManagement.models import Instructor, Student
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from datetime import datetime
from django.utils import timezone
import random


###########

class Course(models.Model):
    name = models.CharField(max_length=200)
    caption = models.CharField(max_length=100)
    price = models.IntegerField()
    discount_percentage = models.SmallIntegerField()

    @property
    def batch(self):return self.batches.filter(completed=False).count()

    archive = models.BooleanField(default=False)
    popular = models.BooleanField(default=False)
    premium = models.BooleanField(default=False)

    pre_recorded = models.BooleanField(default=False)

    lectures = models.SmallIntegerField()
    class_duration = models.CharField(max_length=5, help_text="please input here in format: hh:mm")
    course_duration = models.SmallIntegerField()
    course_duration_in_months = models.SmallIntegerField(null=True, blank=True)
    projects = models.SmallIntegerField()
    mobile_computer = models.BooleanField(default=True)
    certificate = models.BooleanField(default=True)

    short_description = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()

    author_name = models.CharField(max_length=50)
    author_message = models.TextField(null=True, blank=True)
    author_photo = models.ImageField(upload_to="course_author_photos", default='default.png')

    thumbnail = models.FileField(upload_to="course_thumbnails")
    demo_video = models.URLField(null=True, blank=True)
    
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    eligibility = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=255, null=True, blank=True)
    revoke_duration_in_days = models.IntegerField(help_text="input count as day", null=True, blank=True)
    certificate_count = models.SmallIntegerField(null=True, blank=True)
    certificate_no = models.CharField(max_length=8, null=True, blank=True)

    def generate_unique_code(self):
        while True:
            # Generate a random 8-digit number
            code = str(random.randint(10000000, 99999999))
            # Check if the code is unique
            if not Course.objects.filter(certificate_no=code).exists():
                return code

    def save(self, *args, **kwargs):
        # Assign a unique code if not already assigned
        if not self.certificate_no:
            self.certificate_no = self.generate_unique_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class EmiDetails(models.Model):
    emi_type = models.TextField()
    instament_number = models.IntegerField()
    total_payment = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="emi_details")
    emi_duration = models.IntegerField(null=True, blank=True, help_text='Enter the duration between two EMIs in days')

    def __str__(self):
        return f"{self.emi_type} - {self.course.name}"

class InstamentDetails(models.Model):
    emi_type = models.ForeignKey(EmiDetails, on_delete=models.CASCADE, related_name="emi_variation")
    instalment = models.IntegerField()
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.emi_type.emi_type} - {self.instalment} - {self.amount}"

class Week(models.Model):
    name = models.CharField(max_length=50, help_text="Week number or Week Name")
    week = models.IntegerField(null=True, blank=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="syllabi")
    lock = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class CourseAdvantage(models.Model):
    point = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="advantages")
    def __str__(self):
        return f"{self.course.name} -> {self.point}"
    
class CourseInclude(models.Model):
    include = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="includes")
    
    def __str__(self):
        return f"{self.course.name} -> {self.include}"

class CourseIncludeTopic(models.Model):
    topic = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_topics")
    
    def __str__(self):
        return f"{self.course.name} -> {self.topic}"

class CourseCaption(models.Model):
    caption = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_caption")
    
    def __str__(self):
        return f"{self.course.name} -> {self.caption}"

class CourseTopic(models.Model):
    name = models.CharField(max_length=255)
    course = models.ManyToManyField(Course)
    
    def __str__(self):
        # Create a list of course names
        course_names = ", ".join(course.name for course in self.course.all())
        return f"{self.name} -> {course_names}"

########

class Topic(models.Model):
    name = models.CharField(max_length=64)
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name="lessons")
    duration = models.DurationField(choices=(
        (timedelta(minutes=30),'30 min'),
        (timedelta(hours=1),'1 Hr'),
        (timedelta(hours=1, minutes=30),'1 Hr 30 min'),
        (timedelta(hours=2),'2 Hr'),
        (timedelta(hours=2, minutes=30),'2 Hr 30 min'),
        (timedelta(hours=3),'3 Hr'),
    ), null=True, blank=True)
    day = models.CharField(max_length=1, choices=(
        ("1", "Day 1"),
        ("2", "Day 2"),
        ("3", "Day 3"),),null=True, blank=False)
    link = models.URLField(null=True, blank=True)

    def __str__(self) -> str:return self.name

class ProjectName(models.Model):
    project_name = models.TextField(null =True,blank=True)
    def __str__(self) -> str:return f"{self.project_name}"

class ProjectTopic(models.Model):
    project_topic = models.TextField(null =True,blank=True)
    project_name = models.ManyToManyField(ProjectName,help_text="After each eg press enter twice to create new project")
    def get_project_name(self):
        return [i["project_name"] for i in self.project_name.all().values("project_name")]
    def __str__(self) -> str:return f"TopicName : {self.project_topic}, ProjectName : {self.get_project_name()}"

class Batch(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="batches")
    project_topics = models.ManyToManyField(ProjectTopic, blank=True) #new add field
    max_participants = models.SmallIntegerField(default=30)

    start_date = models.DateField(null=True, blank=True,verbose_name="Batch Start Date")
    link = models.URLField(null=True, blank=True)

    completed = models.BooleanField(default=False,verbose_name="Batch Completed")
    end_date = models.DateField(null=True, blank=True,verbose_name="Batch End Date")
    revoke_date = models.DateField(null=True, blank=True,verbose_name="Batch Revoke Date")
    b_certificate = models.BooleanField(default=False,verbose_name="Batch Certificate Release")
    revoke_days = models.IntegerField(help_text="input count as day", null=True, blank=True)
    instructor = models.ForeignKey(Instructor, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='batches')
    students = models.ManyToManyField(Student, related_name='batches', blank=True, through='BatchJoined')

    @property
    def enrolled(self) -> str:
        return f"{self.students.count()} / {self.max_participants}"

    @property
    def name(self) -> str:
        return f"Batch {self.pk} - {self.course.name}"

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = "batches"
    
    def save(self, *args, **kwargs):
        # If revoke_days is not set, use the revoke_duration_in_days from the related course
        if not self.revoke_days and self.course.revoke_duration_in_days:
            self.revoke_days = self.course.revoke_duration_in_days

        if self.end_date and isinstance(self.end_date, str):
            # Assuming end_date is in 'YYYY-MM-DD' format
            self.end_date = datetime.strptime(self.end_date, '%Y-%m-%d').date()

        # Automatically calculate revoke_date when end_date is set and revoke_days are available
        if self.end_date and self.revoke_days:
            self.revoke_date = self.end_date + timedelta(days=self.revoke_days)

        # Check if the b_certificate was previously False and is now being updated to True
        if self.pk:
            previous = Batch.objects.get(pk=self.pk)
            if not previous.b_certificate and self.b_certificate:
                self.on_certificate_release()

        # Call the original save method
        super().save(*args, **kwargs)


    def on_certificate_release(self):
        title = "Certificate unlocked"
        current_date = datetime.now().strftime("%d-%m-%Y")
        message = f"Your {self.course.name} is complete. Please download your certificate from the Certificates section.\nDate : {current_date}"
        send_notification_to_batch(self.id, title, message)
        print(f"Batch {self.id}: Certificate released.")

from freeCourseManagement.helpers import notify_user

def send_notification_to_batch(batch_id, title, message):
    batch = Batch.objects.get(id=batch_id)
    students = batch.students.all()
    for std in students:
        user_id = std.user.id
        notify_user(user_id, title, message)
    return True

class BatchJoined(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="joined_batches")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="joined_students")
    payment_id = models.CharField(max_length=50, null=True, blank=True)
    assign_topics = models.ManyToManyField(ProjectTopic, blank=True)
    assign_projects = models.ManyToManyField(ProjectName, blank=True)
    full_payment_status = models.BooleanField(default=False)
    choice_emi_type = models.ForeignKey(EmiDetails, on_delete=models.CASCADE, null=True, blank=True)
    total_payment = models.IntegerField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.batch.name}"

PAYMENT_MODE = (
                ("",""),
                ("manual_entry", "manual_entry"),
                ("online_entry", "online_entry")
                )

class StudentEmi(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="payment_students")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="payment_students")
    amount = models.IntegerField()
    emi_number = models.IntegerField()
    payment_mode =  models.CharField(max_length=15, choices=PAYMENT_MODE, default="")
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.BooleanField(default=False)
    payment_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    json_response = models.JSONField(null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.student.user.username} || {self.amount} || {self.emi_number} || Batch:-{self.batch.id} || Payment Status:- {self.payment_status}"

    def update_total_payment(self):
        check_batch_std_choice_emi_type = BatchJoined.objects.filter(batch=self.batch, student=self.student)
        if check_batch_std_choice_emi_type.exists():
            batch_joined = check_batch_std_choice_emi_type.first()
            choice_emi_type = batch_joined.choice_emi_type
            if self.emi_number <= choice_emi_type.instament_number:
                # print("enter")
                if self.payment_status:
                    total_paid = StudentEmi.objects.filter(student=self.student, batch=self.batch, payment_status=True).aggregate(total_paid=Sum('amount'))['total_paid']
                    # print("sgdfhg", total_paid)
                    if not total_paid:
                        total_paid = 0
                    # Check if the total paid matches the total payment required
                    if total_paid >= choice_emi_type.total_payment:
                        batch_joined.full_payment_status = True
                        batch_joined.total_payment = total_paid
                        batch_joined.save()
                    else:
                        batch_joined.full_payment_status = False
                        batch_joined.total_payment = total_paid
                        batch_joined.save()

        else:
            raise ValidationError(f"BatchJoined entry not found for student {self.student} and batch {self.batch}.")
        

@receiver(post_delete, sender=StudentEmi)
@receiver(post_save, sender=StudentEmi)
def update_batch_joined_total_payment(sender, instance, **kwargs):
    instance.update_total_payment()

class TimeTable(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="timetable")

    topic = models.CharField(max_length=128, null=True, blank=True)

    start_time = models.TimeField()
    start_date = models.DateField()

    end_time = models.TimeField(null=True, blank=False)

    link = models.URLField(null=True, blank=True)
    week = models.CharField(max_length=2, choices=(
        ("1", "Week 1"),
        ("2", "Week 2"),
        ("3", "Week 3"),
        ("4", "Week 4"),
        ("5", "Week 5"),
        ("6", "Week 6"),
        ("7", "Week 7"),
        ("8", "Week 8"),
        ("9", "Week 9"),
        ("10", "Week 10"),
        ("11", "Week 11"),
        ("12", "Week 12"),
        ("13", "Week 13"),
        ("14", "Week 14"),
        ("15", "Week 15"),
        ("16", "Week 16"),
        ("17", "Week 17"),
        ("18", "Week 18"),
        ("19", "Week 19"),
        ("20", "Week 20"),
        ("21", "Week 21"),
        ("22", "Week 22"),
        ("23", "Week 23"),
        ("24", "Week 24"),
        ("25", "Week 25"),
        ("26", "Week 26"),
        ("27", "Week 27"),
        ("28", "Week 28"),
        ("29", "Week 29"),
        ("30", "Week 30"),
        ("31", "Week 31"),
        ("32", "Week 32"),
        ("33", "Week 33"),
        ("34", "Week 34"),
        ("35", "Week 35"),
        ("36", "Week 36"),
        ("37", "Week 37"),
        ("38", "Week 38"),
        ("39", "Week 39"),
        ("40", "Week 40"),
        ("41", "Week 41"),
        ("42", "Week 42"),
        ("43", "Week 43"),
        ("44", "Week 44"),
        ("45", "Week 45"),
        ("46", "Week 46"),
        ("47", "Week 47"),
        ("48", "Week 48"),
        ("49", "Week 49"),
        ("50", "Week 50"),
        ("51", "Week 51"),
        ("52", "Week 52"),
    ),null=True, blank=False)
    day = models.CharField(max_length=1, choices=(
        ("1", "Day 1"),
        ("2", "Day 2"),
        ("3", "Day 3"),),null=True, blank=False)

    def save(self, *args, **kwargs):        
        course_duration = self.batch.course.course_duration
     
        if int(self.week) == course_duration and self.day == "3":          
            self.batch.end_date = self.start_date
            self.batch.save()  
            
        super().save(*args, **kwargs)

    def __str__(self) -> str:return f"{self.batch.name} - {self.start_date}"
        
class Note(models.Model):
    topic = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    week = models.CharField(max_length=2, choices=(
        ("1", "Week 1"),
        ("2", "Week 2"),
        ("3", "Week 3"),
        ("4", "Week 4"),
        ("5", "Week 5"),
        ("6", "Week 6"),
        ("7", "Week 7"),
        ("8", "Week 8"),
        ("9", "Week 9"),
        ("10", "Week 10"),
        ("11", "Week 11"),
        ("12", "Week 12"),
        ("13", "Week 13"),
        ("14", "Week 14"),
        ("15", "Week 15"),
        ("16", "Week 16"),
        ("17", "Week 17"),
        ("18", "Week 18"),
        ("19", "Week 19"),
        ("20", "Week 20"),
        ("21", "Week 21"),
        ("22", "Week 22"),
        ("23", "Week 23"),
        ("24", "Week 24"),
        ("25", "Week 25"),
        ("26", "Week 26"),
        ("27", "Week 27"),
        ("28", "Week 28"),
        ("29", "Week 29"),
        ("30", "Week 30"),
        ("31", "Week 31"),
        ("32", "Week 32"),
        ("33", "Week 33"),
        ("34", "Week 34"),
        ("35", "Week 35"),
        ("36", "Week 36"),
        ("37", "Week 37"),
        ("38", "Week 38"),
        ("39", "Week 39"),
        ("40", "Week 40"),
        ("41", "Week 41"),
        ("42", "Week 42"),
        ("43", "Week 43"),
        ("44", "Week 44"),
        ("45", "Week 45"),
        ("46", "Week 46"),
        ("47", "Week 47"),
        ("48", "Week 48"),
        ("49", "Week 49"),
        ("50", "Week 50"),
        ("51", "Week 51"),
        ("52", "Week 52"),
    ))
    file = models.FileField(upload_to="course_notes")

    def __str__(self) -> str:return f"{self.topic}"        


class EmiReminderStatusLog(models.Model):
    status = models.BooleanField(default=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='mail_user')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='batch_emi')
    send_at = models.DateTimeField(auto_now_add=True)
    emi_number = models.IntegerField(null=True, blank=True)
    emi_amount = models.IntegerField(null=True, blank=True)
    reminder_date = models.DateField(default=timezone.now)  

    def __str__(self):
        return f'{self.student.user.first_name} {self.student.user.last_name} || {self.batch.name} || EMI number- {self.emi_number} || Email status - {self.status}'