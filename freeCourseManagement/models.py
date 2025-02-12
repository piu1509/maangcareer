from django.db import models
from userManagement.models import *
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import requests
import json
import os
from django.utils import timezone
import random


# Create your models here.

class FreeCourse(models.Model):
    name = models.CharField(max_length=200)
    caption = models.CharField(max_length=100)   
    serial_no = models.IntegerField(null=True, blank=True)

    archive = models.BooleanField(default=False)
    popular = models.BooleanField(default=False)

    pre_recorded = models.BooleanField(default=False)
    course_duration_title = models.CharField(max_length=255, null=True, blank=True)
    projects = models.SmallIntegerField()
    section_number = models.PositiveIntegerField(editable=False)
    mobile_computer = models.BooleanField(default=True)
    certificate = models.BooleanField(default=True)

    short_description = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()

    author_name = models.CharField(max_length=50)
    author_message = models.TextField(null=True, blank=True)
    author_photo = models.ImageField(upload_to="free_course_author_photos", default='default.png')

    thumbnail = models.FileField(upload_to="free_course_thumbnails")
    demo_video = models.URLField(null=True, blank=True)
    average_quiz_score = models.FloatField(default=75.0, help_text="Minimum average quiz score for certificate.")
    average_practice_score = models.FloatField(default=75.0, help_text="Minimum average practice score for certificate.")
    average_mock_score = models.FloatField(default=75.0, help_text="Minimum average mock score for certificate.")
    certificate_no = models.CharField(max_length=8, null=True, blank=True)

    def generate_unique_code(self):
        while True:
            # Generate a random 8-digit number
            code = str(random.randint(10000000, 99999999))
            # Check if the code is unique
            if not FreeCourse.objects.filter(certificate_no=code).exists():
                return code

    def save(self, *args, **kwargs):
        # Assign a unique code if not already assigned
        if not self.certificate_no:
            self.certificate_no = self.generate_unique_code()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["serial_no"]

    def __str__(self):
        return self.name
    

class FreeCourseAdvantage(models.Model):
    point = models.TextField()
    course = models.ForeignKey(FreeCourse, on_delete=models.CASCADE, related_name="free_course_advantages")

    def __str__(self):
        return f"{self.course.name} -> {self.point}"
    
    
class FreeCourseInclude(models.Model):
    include = models.TextField()
    course = models.ForeignKey(FreeCourse, on_delete=models.CASCADE, related_name="free_course_includes")
    
    def __str__(self):
        return f"{self.course.name} -> {self.include}"
    

class FreeCourseIncludeTopic(models.Model):
    topic = models.TextField()
    course = models.ForeignKey(FreeCourse, on_delete=models.CASCADE, related_name="free_course_topics")
    
    def __str__(self):
        return f"{self.course.name} -> {self.topic}"
    

class FreeCourseCaption(models.Model):
    caption = models.TextField()
    course = models.ForeignKey(FreeCourse, on_delete=models.CASCADE, related_name="free_course_caption")
    
    def __str__(self):
        return f"{self.course.name} -> {self.caption}"

    
class FreeCourseSyllabus(models.Model):
    course = models.ForeignKey(FreeCourse, on_delete=models.CASCADE, related_name="course_syllabus")
    number = models.PositiveIntegerField(editable=False)  # Make this field non-editable
    name = models.CharField(max_length=255)
    max_attempts = models.PositiveIntegerField(default=50, help_text="Maximum number of time a student can attempt the questions.")
    max_score = models.FloatField(default=75.0, help_text="Minimum passing percentage")
    time_duration = models.DurationField(null=True, blank=True)
    number_of_questions = models.PositiveIntegerField(null=True, blank=True)
    max_score_practice = models.FloatField(default=75.0, help_text="Minimum passing percentage")
    max_attempts_mock = models.PositiveIntegerField(default=50, help_text="Maximum number of time a student can attempt the questions.")
    max_score_mock = models.FloatField(default=75.0, help_text="Minimum passing percentage")
    time_duration_mock = models.DurationField(null=True, blank=True)

    class Meta:
        ordering = ["number"]

    def save(self, *args, **kwargs):
        if not self.pk:
            last_syllabus = FreeCourseSyllabus.objects.filter(course=self.course).order_by('number').last()
            self.number = last_syllabus.number + 1 if last_syllabus else 1
        super().save(*args, **kwargs)

        self.course.section_number = FreeCourseSyllabus.objects.filter(course=self.course).count()
        self.course.save()
    
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.course.section_number = FreeCourseSyllabus.objects.filter(course=self.course).count()
        self.course.save()

    def __str__(self):
        return f"{self.course.name} - {self.name}"

@receiver(post_delete, sender=FreeCourseSyllabus)
def update_section_number_on_delete(sender, instance, **kwargs):
    instance.course.section_number = FreeCourseSyllabus.objects.filter(course=instance.course).count()
    instance.course.save()

@receiver(post_delete, sender=FreeCourseSyllabus)
def reorder_syllabus_numbers(sender, instance, **kwargs):
    syllabi = FreeCourseSyllabus.objects.filter(course=instance.course).order_by('number')
    for index, syllabus in enumerate(syllabi):
        syllabus.number = index + 1
        syllabus.save()


class SyllabusTopics(models.Model):
    section = models.ForeignKey(FreeCourseSyllabus, on_delete=models.CASCADE, related_name="syllabus_topics")
    title = models.CharField(max_length=255)
    number = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='free_course_syllabus', null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return f"{self.section.name} - {self.title}"
    

class FreeCourseJoinee(models.Model):
    course = models.ForeignKey(FreeCourse, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    is_completed = models.BooleanField(default=False, blank=True)
    is_certificate = models.BooleanField(default=False, blank=True)
    certificate = models.FileField(upload_to='free_course_certificates', null=True, blank=True)
    is_released = models.BooleanField(default=True)
    score = models.PositiveIntegerField(null=True, blank=True)
    grade = models.CharField(max_length=10, null=True, blank=True) 
    joined_at = models.DateTimeField(auto_now_add=True, null=True, blank=True) 
    end_date = models.DateTimeField(null=True, blank=True, help_text="Course completion date") 

    def save(self, *args, **kwargs):
        if self.is_completed and not self.end_date:
            self.end_date = timezone.now()
        super().save(*args, **kwargs)

    def _str_(self):
        return f"{self.course.name}"


class CourseSectionQuestion(models.Model):
    course_section = models.ForeignKey(FreeCourseSyllabus, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Course Syllabus"
        verbose_name_plural = "Section Quiz Questions"

    def __str__(self):
        return f"Questions for {self.course_section.name}"

ANSWER_CHOICES = (
    ('option1','option1'),
    ('option2','option2'),
    ('option3','option3'),
    ('option4','option4')
)
class FreeCourseQuizQuestion(models.Model):
    course_section_question = models.ForeignKey(CourseSectionQuestion, related_name='quiz_questions', on_delete=models.CASCADE)
    topic = models.ForeignKey(SyllabusTopics, on_delete=models.CASCADE,null=True, blank=True, related_name="question_topic")
    question = models.CharField(max_length=255)
    option1 = models.TextField(null=True, blank=True)
    option2 = models.TextField(null=True, blank=True)
    option3 = models.TextField(null=True, blank=True)
    option4 = models.TextField(null=True, blank=True)
    answer = models.CharField(max_length=10, choices=ANSWER_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.question} - {self.question}"


class QuizQuestionAttempts(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attempted_student")
    course = models.ForeignKey(FreeCourse, on_delete=models.CASCADE, related_name="course_questions")
    syllabus = models.ForeignKey(FreeCourseSyllabus, on_delete=models.CASCADE, related_name="syllabus_questions")
    attempt_number = models.PositiveIntegerField()
    attempt_answer = models.JSONField(null=True, blank=True)
    attempt_score = models.FloatField(null=True, blank=True)
    is_passed = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)
    right_answers = models.PositiveIntegerField(null=True, blank=True, help_text="Number of right answers..")
    wrong_answers = models.PositiveIntegerField(null=True, blank=True, help_text="Number of wrong answers..")

    def __str__(self):
        return f"{self.course.name} - Section :{self.syllabus.number} : {self.student.user.username} - {self.attempt_number} attempt."
    

class FreeCourseCompilerQuestion(models.Model):
    disable = models.BooleanField(default=False)
    practice_mock = models.BooleanField(default=False, help_text="False is 'Practice Question'; True is 'Mock Test Question'")
    def practice_or_mock(self) -> str: return "Practice" if not self.practice_mock else "Mock"   
    
    course_section = models.ForeignKey(FreeCourseSyllabus, related_name='compiler_questions',null=True, blank=True, on_delete=models.CASCADE)
    topic = models.ForeignKey(SyllabusTopics, on_delete=models.CASCADE,null=True, blank=True, related_name="compiler_question_topic")   
    question_number = models.CharField(max_length=2)
    ques_title = models.CharField(max_length=255, verbose_name="Question Title")

    # Compnay TAGS

    google = models.BooleanField(default=True)
    amazon = models.BooleanField(default=True)
    microsoft = models.BooleanField(default=True)
    meta = models.BooleanField(default=True)
    linkedin = models.BooleanField(default=True)
    uber = models.BooleanField(default=True)
    adobe = models.BooleanField(default=True)
    cred = models.BooleanField(default=True)

    # Problems

    prob_text = models.TextField()
    prob_pic = models.ImageField(upload_to='free_course_quesion_pictures',null=True, blank=True) #qus_pic

    examples = models.TextField(help_text="After each eg press enter twice to create new example" ,null=True, blank=True)
    
    constraints = models.TextField(help_text="After each eg press enter twice to create new constraint" ,null=True, blank=True)
    const_pic = models.ImageField(upload_to="free_course_constraints_pictures",null=True, blank=True)
    challenge = models.TextField(null=True, blank=True)
    video_solutions = models.TextField(help_text="After each eg press enter twice to create new video link" ,null=True, blank=True)
    
    test_cases = models.JSONField(null=True, blank=True, default=dict)
    test_cases_to_view = models.JSONField(default=dict, blank=True)
    
    def __str__(self) :
        return f"{self.ques_title} - Mock " if self.practice_mock else f"{self.ques_title} - Practice "


class FreeCourseCompilerQuestionExampleImage(models.Model):
    question = models.ForeignKey(FreeCourseCompilerQuestion, on_delete=models.CASCADE, null=True,blank=True, related_name="free_course_com_ques_ex_image")  
    example_name = models.CharField(max_length=255, null=True, blank=True)
    example_picture = models.ImageField(upload_to='free_course_example_pictures/', null=True, blank=True) 

    def __str__(self):
        return f"Example images for {self.question.ques_title}"


class FreeCourseCompilerQuestionApproach(models.Model):
    question = models.ForeignKey(FreeCourseCompilerQuestion, on_delete=models.CASCADE, null=True,blank=True, related_name="free_course_compiler_question_approach")
    approach_title = models.CharField(max_length=255, null=True, blank=True)
    approach_intuition = models.TextField(null=True, blank=True)
    approach_algo = models.TextField(null=True, blank=True) 
    approach_complexity_analysis = models.TextField(null=True, blank=True) 

    def __str__(self):
        return f"{self.question.ques_title} - {self.approach_title}"


class FreeCourseCompilerQuestionApproachImage(models.Model):
    approach = models.ForeignKey(FreeCourseCompilerQuestionApproach, on_delete=models.CASCADE, related_name="free_question_approach_image")
    pic = models.ImageField(upload_to='free_course_approach_pictures', null=True, blank=True, verbose_name="Pic ")

    def __str__(self):
        return f"{self.approach.approach_title} - {self.pic}" 


class FreeCourseCompilerQuestionApproachCode(models.Model):
    approach = models.ForeignKey(FreeCourseCompilerQuestionApproach, on_delete=models.CASCADE, related_name="free_question_approach_code")
    language = models.CharField(max_length=25)
    code = models.TextField()

    def __str__(self):
        return f"{self.approach.approach_title} - {self.language}"
    

class FreeCourseCompilerQuestionLoadTemplate(models.Model):
    load_template = models.TextField(null=True, blank=True)   
    
    @staticmethod
    def get_compiler():
        res = []       
        file_path = os.path.join('judge0_languages.json')  # Adjust path if necessary
        with open(file_path, 'r') as file:
            data = json.load(file)["language_data"]
        
        for compiler in data:
            
            choice_name = f"{compiler.get("name")} || {compiler.get("id")}"
            res.append((choice_name, choice_name))
            
        return tuple(res)
                

    compiler = models.CharField(max_length=255, choices=get_compiler(), null=True,blank=True)
    question = models.ForeignKey(FreeCourseCompilerQuestion, on_delete=models.CASCADE, null=True,blank=True, related_name="free_course_com_ques")
    def __str__(self) :
        return f"{self.question}, ID : " + f"{self.compiler}".split("||")[0]
    

class FreeCourseCompilerQuestionAttempt(models.Model):
    question = models.ForeignKey(FreeCourseCompilerQuestion, on_delete=models.CASCADE, related_name="attempted_ques")
    student = models.ForeignKey(Student, on_delete=models.CASCADE,null=True,blank=True, related_name="attempting_student")
    course = models.ForeignKey(FreeCourse, on_delete=models.CASCADE, related_name="course_compiler_questions")
    syllabus = models.ForeignKey(FreeCourseSyllabus, on_delete=models.CASCADE, related_name="syllabus_compiler_questions")
    status = models.BooleanField(default=False)
    submitted = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)
    attepmt_number = models.PositiveBigIntegerField(blank=True, null=True, default=0)
    load_template = models.ForeignKey(FreeCourseCompilerQuestionLoadTemplate, on_delete=models.CASCADE, null=True, blank=True, related_name="com_ques_template")
    coding_language = models.CharField(max_length=255, help_text="Language", null=True,blank=True)
    student_ans = models.TextField(help_text="Student Code", null=True,blank=True)
    code_response_status = models.JSONField(null=True, blank=True, default=dict)
    code_response = models.TextField(help_text="Response from judge0", null=True,blank=True)
    button_clicked =  models.CharField(max_length=11, choices=(
        ('Run', 'Run'),
        ('Submit','Submit')
    ), null=True,blank=True)
    score = models.PositiveBigIntegerField(null=True , blank=True, default=0)
    practic_time = models.DateTimeField(auto_now=True)

    def __str__(self) :        
        return f"{self.question}, {self.student.user.first_name}  {self.student.user.last_name}"


class SavePracticeCompilerQuestionCode(models.Model):
    template = models.ForeignKey(FreeCourseCompilerQuestionLoadTemplate, on_delete=models.CASCADE, related_name="saved_template")
    student = models.ForeignKey(Student, on_delete=models.CASCADE,null=True,blank=True)
    code_text = models.TextField()
    autosave_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.user.username}||{self.template.compiler}"    

@receiver(post_save, sender=SavePracticeCompilerQuestionCode)
def update_load_template_on_save(sender, instance, **kwargs):
    instance.template.load_template = instance.code_text
    instance.template.save()

@receiver(post_delete, sender=SavePracticeCompilerQuestionCode)
def update_load_template_on_delete(sender, instance, **kwargs):
    instance.template.load_template = "#Write your code here..."
    instance.template.save()    

# class TrackPracticeAttempt(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE,null=True,blank=True, related_name="practice_student")
#     course_section = models.ForeignKey(FreeCourseSyllabus, on_delete=models.CASCADE, related_name="section_practice_attempt")
#     attempt_number = 


class MockCompilerQuestionResult(models.Model):
    course = models.ForeignKey(FreeCourse, on_delete=models.CASCADE, related_name="course_mock_question_result")
    course_section = models.ForeignKey(FreeCourseSyllabus, on_delete=models.CASCADE, related_name="syllabus_mock_result", null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_mock_result")
    questions = models.JSONField(null=True, blank=True)
    attempt_number = models.IntegerField()  
    score = models.IntegerField(null=True , blank=True, default=0) 
    is_passed = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)
    right_answers = models.PositiveIntegerField(null=True, blank=True, help_text="Number of right answers..")
    wrong_answers = models.PositiveIntegerField(null=True, blank=True, help_text="Number of wrong answers..")
    
    def __str__(self) :
        return f"{self.student.user.first_name} {self.student.user.last_name} - {self.student.user.username}-{self.course.name}: {self.course_section.name}"
    

    