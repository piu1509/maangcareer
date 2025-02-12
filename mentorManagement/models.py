from django.db import models
from courseManagement.models import Course
from testsManagement.models import *
from userManagement.models import *
# Create your models here.



class Syllabus(models.Model):
    week = models.CharField(max_length=2,choices=(
        ('1', 'Week 1'),
        ('2', 'Week 2'),
        ('3', 'Week 3'),
        ('4', 'Week 4'),
        ('5', 'Week 5'),
        ('6', 'Week 6'),
        ('7', 'Week 7'),
        ('8', 'Week 8'),
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
    day = models.CharField(max_length=1, choices=(
        ('1','Day 1'),
        ('2','Day 2'),
        ('3','Day 3'),
    ))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True,blank=True)
    topic = models.CharField(max_length=128, null=True, blank=True)
    # file = models.FileField(upload_to='upload_task')
    file = models.FileField(upload_to='upload_task' , blank=True)
    description = TextField(null=True, blank=False)
    uploaded_at = models.DateTimeField(auto_now=True)                                             
    
    def __str__(self) :
        return f"Course -> {self.course.name}, Week-> {self.week}, Topic-> {self.topic}" 
    

class BatchCompleteRequest(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    is_complete = models.CharField(max_length=30, choices=(
        ('pending', 'Pending'),
        ('approved', 'Approved'), 
        ('rejected', 'Rejected'),
    ), default='pending')
    send_email_for_certification = models.BooleanField(default=False)

    def __str__(self) :
        return f"Batch{self.batch.id} || {self.instructor.user.username} || {self.request_date.date()} || {self.is_complete}"    