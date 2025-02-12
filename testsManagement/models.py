from django.db.models import (
    Model,

    ForeignKey,
    ManyToManyField,
    TextField,
    JSONField,
    DateTimeField,
    CharField,
    BooleanField,

    ImageField,
    URLField,
    PositiveSmallIntegerField,
    TimeField,
    PositiveBigIntegerField,
    FileField,

    CASCADE
)
from courseManagement.models import *
from userManagement.models import *
import requests, json, os


class Quiz(Model):
    name = CharField(max_length=256)
    course = ForeignKey(Course, on_delete=CASCADE)
    students = ManyToManyField(Student, through='QuizAttempt')

    week = CharField(max_length=2,choices=(
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

    def __str__(self) -> str:
        # return self.name if len(self.name) < 30 else f"{self.name[:27]}..."
        return f"{self.name} [{self.course}], week {self.week}"

class QuizQuestion(Model):
    quiz = ForeignKey(Quiz, on_delete=CASCADE)
    question = TextField()
    answers = JSONField()

    def __str__(self) -> str:
        return self.question if len(self.question) < 30 else f"{self.question[:27]}..."

class QuizAttempt(Model):
    quiz = ForeignKey(Quiz, on_delete=CASCADE)
    student = ForeignKey(Student, on_delete=CASCADE)
    questions = ManyToManyField(QuizQuestion)
    passed = BooleanField(default=False)
    score = CharField(max_length=3, blank=True, null=True)
    date = DateTimeField(auto_now_add=True)
    answers = JSONField(default=None, blank=True, null=True)
    attempts = PositiveSmallIntegerField(default=1)

    def __str__(self) :
        return f"{self.student.user.first_name} {self.student.user.last_name} - {self.student.user.username} - {self.quiz.course.name} - week {self.quiz.week}"

# class CompilerQuestion(Model):
#     disable = BooleanField(default=False)
#     practice_mock = BooleanField(default=False, help_text="False is 'Practice Question'; True is 'Mock Test Question'")
#     def practice_or_mock(self) -> str: return "Practice" if not self.practice_mock else "Mock"
#     week = CharField(max_length=1, choices=(
#         ('1','Week 1'),
#         ('2','Week 2'),
#         ('3','Week 3'),
#         ('4','Week 4'),
#         ('5','Week 5'),
#         ('6','Week 6'),
#         ('7','Week 7'),
#         ('8','Week 8'),
#     ))
#     day = CharField(max_length=1, choices=(
#         ('1','Day 1'),
#         ('2','Day 2'),
#         ('3','Day 3'),
#     ))
#     question_number = CharField(max_length=2)

#     # languages = CharField(max_length=1, choices=(
#     #     ('c', 'C++'),
#     #     ('j','JAVA'),
#     #     ('p','Python')
#     # ))

#     ###
#     # Problem

#     ques_title = CharField(max_length=255, verbose_name="Question Title")

#     ###
#     # Compnay TAGS

#     google = BooleanField(default=True)
#     amazon = BooleanField(default=True)
#     microsoft = BooleanField(default=True)
#     meta = BooleanField(default=True)
#     linkedin = BooleanField(default=True)
#     uber = BooleanField(default=True)
#     adobe = BooleanField(default=True)
#     cred = BooleanField(default=True)

#     ###
#     # Problems

#     prob_text = TextField()
#     ques_pic = ImageField(upload_to='quesion_pictures')
#     const_pic = ImageField(upload_to='constraints_pictures')

#     examples = TextField(help_text="After each eg press enter twice to create new example")
#     test_case = TextField(default ="null", null=True,blank=True, help_text="After each eg press enter twice to create new cases")
#     ###
#     # Hint

#     hint_video = URLField()
#     hint_theory = TextField()
#     hint_pic = ImageField(upload_to='hint_pictures')
#     hint_code = TextField(help_text="After each code press enter twice to create new code hint")

#     ###
#     # Submissions

#     students = ManyToManyField(Student, through='CompilerQuestionAtempt')
#     # New Field added
#     prob_id = CharField(max_length=255, help_text="Question Id from sphere-engine", null=True,blank=True)
#     course = ForeignKey(Course, on_delete=CASCADE, null=True,blank=True)
#     def __str__(self) :
#         return f"Mock - {self.ques_title}" if self.practice_mock else f"Practice - {self.ques_title}"

# modified CompilerQuestion model

class CompilerQuestion(Model):
    disable = BooleanField(default=False)
    practice_mock = BooleanField(default=False, help_text="False is 'Practice Question'; True is 'Mock Test Question'")
    def practice_or_mock(self) -> str: return "Practice" if not self.practice_mock else "Mock"
    week = CharField(max_length=2, choices=(
        ('1','Week 1'),
        ('2','Week 2'),
        ('3','Week 3'),
        ('4','Week 4'),
        ('5','Week 5'),
        ('6','Week 6'),
        ('7','Week 7'),
        ('8','Week 8'),
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
    day = CharField(max_length=1, choices=(
        ('1','Day 1'),
        ('2','Day 2'),
        ('3','Day 3'),
    ),null= True ,  blank= True)
    # day = CharField(max_length=1, choices=(
    #     ('1','Day 1'),
    #     ('2','Day 2'),
    #     ('3','Day 3'),
    # ))
    course = ForeignKey(Course, on_delete=CASCADE, null=True,blank=True)
    prob_id = CharField(max_length=255, help_text="Question Id from sphere-engine", null=True,blank=True)
    question_number = CharField(max_length=2)

    # languages = CharField(max_length=1, choices=(
    #     ('c', 'C++'),
    #     ('j','JAVA'),
    #     ('p','Python')
    # ))

    ###
    # Problem

    ques_title = CharField(max_length=255, verbose_name="Question Title")

    ###
    # Compnay TAGS

    google = BooleanField(default=True)
    amazon = BooleanField(default=True)
    microsoft = BooleanField(default=True)
    meta = BooleanField(default=True)
    linkedin = BooleanField(default=True)
    uber = BooleanField(default=True)
    adobe = BooleanField(default=True)
    cred = BooleanField(default=True)

    ###
    # Problems

    prob_text = TextField()
    prob_pic = ImageField(upload_to='quesion_pictures',null=True, blank=True) #qus_pic

    examples = TextField(help_text="After each eg press enter twice to create new example" ,null=True, blank=True)
    check_exm_pic1 = BooleanField(default=False)
    example1_picture = ImageField(upload_to='example1_pictures/', null=True, blank=True)
    check_exm_pic2 = BooleanField(default=False)
    example2_picture = ImageField(upload_to='example2_pictures/', null=True, blank=True)
    check_exm_pic3 = BooleanField(default=False)
    example3_picture = ImageField(upload_to='example3_pictures/', null=True, blank=True)
    constraints = TextField(help_text="After each eg press enter twice to create new constraint" ,null=True, blank=True)
    const_pic = ImageField(upload_to="constraints_pictures",null=True, blank=True)
    challenge = TextField(null=True, blank=True)
    video_solutions = TextField(help_text="After each eg press enter twice to create new video link" ,null=True, blank=True)
    # test_case = TextField(default ="null", null=True,blank=True, help_text="After each eg press enter twice to create new cases")
    test_cases = JSONField(null=True, blank=True, default=dict)
    test_cases_to_pass = JSONField(default=dict, blank=True)
    # Approach 1 fields
    approach1_block = BooleanField(default=False)
    approach1_title = CharField(max_length=255,null=True, blank=True)
    approach1_intuition = TextField(null=True, blank=True)
    approach1_algo = TextField(null=True, blank=True)

    approach1_picture_implementation = BooleanField(default=False, verbose_name="Approach1 Picture Implementation")
    check_pic1 = BooleanField(default=False, verbose_name="check Pic 1")
    approach1_pic1 = ImageField(upload_to='approach1_pictures', null=True, blank=True, verbose_name="Pic 1")
    check_pic2 = BooleanField(default=False, verbose_name="check Pic 2")
    approach1_pic2 = ImageField(upload_to='approach1_pictures', null=True, blank=True, verbose_name="Pic 2")
    check_pic3 = BooleanField(default=False, verbose_name="check Pic 3")
    approach1_pic3 = ImageField(upload_to='approach1_pictures', null=True, blank=True, verbose_name="Pic 3")
    check_pic4 = BooleanField(default=False, verbose_name="check Pic 4")
    approach1_pic4 = ImageField(upload_to='approach1_pictures', null=True, blank=True, verbose_name="Pic 4")
    check_pic5 = BooleanField(default=False, verbose_name="check Pic 5")
    approach1_pic5 = ImageField(upload_to='approach1_pictures', null=True, blank=True, verbose_name="Pic 5")

    approach1_code_implementation = BooleanField(default=False, verbose_name="Approach1 Code Implementation")
    approach1_cpp_code = TextField(verbose_name="C++ Code", null=True, blank=True)
    approach1_java_code = TextField(verbose_name="Java Code", null=True, blank=True)
    approach1_python_code = TextField(verbose_name="Python Code", null=True, blank=True)

    approach1_complexity_analysis = TextField( null=True, blank=True)

    # Approach 2 Fields
    approach2_block = BooleanField(default=False)
    approach2_title = CharField(max_length=255, null=True, blank=True)
    approach2_intuition = TextField(null=True, blank=True)
    approach2_algo = TextField(null=True, blank=True)

    approach2_picture_implementation = BooleanField(default=False, verbose_name="Approach2 Picture Implementation")
    check_pic1_approach2 = BooleanField(default=False, verbose_name="Check Pic 1 ")
    approach2_pic1 = ImageField(upload_to='approach2_pictures', null=True, blank=True, verbose_name="Pic 1 ")
    check_pic2_approach2 = BooleanField(default=False, verbose_name="Check Pic 2 ")
    approach2_pic2 = ImageField(upload_to='approach2_pictures', null=True, blank=True, verbose_name="Pic 2 ")
    check_pic3_approach2 = BooleanField(default=False, verbose_name="Check Pic 3 ")
    approach2_pic3 = ImageField(upload_to='approach2_pictures', null=True, blank=True, verbose_name="Pic 3 ")
    check_pic4_approach2 = BooleanField(default=False, verbose_name="Check Pic 4 ")
    approach2_pic4 = ImageField(upload_to='approach2_pictures', null=True, blank=True, verbose_name="Pic 4 ")
    check_pic5_approach2 = BooleanField(default=False, verbose_name="Check Pic 5 ")
    approach2_pic5 = ImageField(upload_to='approach2_pictures', null=True, blank=True, verbose_name="Pic 5 ")

    approach2_code_implementation = BooleanField(default=False, verbose_name="Approach2 Code Implementation")
    approach2_cpp_code = TextField(verbose_name="C++ Code ", null=True, blank=True)
    approach2_java_code = TextField(verbose_name="Java Code ", null=True, blank=True)
    approach2_python_code = TextField(verbose_name="Python Code ", null=True, blank=True)

    approach2_complexity_analysis = TextField(null=True, blank=True)

    # Approach 3 Fields
    approach3_block = BooleanField(default=False)
    approach3_title = CharField(max_length=255, null=True, blank=True)
    approach3_intuition = TextField(null=True, blank=True)
    approach3_algo = TextField(null=True, blank=True)

    approach3_picture_implementation = BooleanField(default=False, verbose_name="Approach3 Picture Implementation")
    check_pic1_approach3 = BooleanField(default=False, verbose_name="Check Pic 1")
    approach3_pic1 = ImageField(upload_to='approach3_pictures', null=True, blank=True, verbose_name="Pic 1 ")
    check_pic2_approach3 = BooleanField(default=False, verbose_name="Check Pic 2 ")
    approach3_pic2 = ImageField(upload_to='approach3_pictures', null=True, blank=True, verbose_name="Pic 2 ")
    check_pic3_approach3 = BooleanField(default=False, verbose_name="Check Pic 3 ")
    approach3_pic3 = ImageField(upload_to='approach3_pictures', null=True, blank=True, verbose_name="Pic 3 ")
    check_pic4_approach3 = BooleanField(default=False, verbose_name="Check Pic 4 ")
    approach3_pic4 = ImageField(upload_to='approach3_pictures', null=True, blank=True, verbose_name="Pic 4 ")
    check_pic5_approach3 = BooleanField(default=False, verbose_name="Check Pic 5 ")
    approach3_pic5 = ImageField(upload_to='approach3_pictures', null=True, blank=True, verbose_name="Pic 5 ")

    approach3_code_implementation = BooleanField(default=False, verbose_name="Approach3 Code Implementation")
    approach3_cpp_code = TextField(verbose_name="C++ Code ", null=True, blank=True)
    approach3_java_code = TextField(verbose_name="Java Code ", null=True, blank=True)
    approach3_python_code = TextField(verbose_name="Python Code ", null=True, blank=True)

    approach3_complexity_analysis = TextField(null=True, blank=True)
    ###
    # Hint
    # hint_video = URLField()
    # hint_theory = TextField()
    # hint_pic = ImageField(upload_to='hint_pictures')
    # hint_code = TextField(help_text="After each code press enter twice to create new code hint")

    ###
    # Submissions
    students = ManyToManyField(Student, through='CompilerQuestionAtempt')
    
    def __str__(self) :
        return f"{self.ques_title} - Mock - Week -{self.week}" if self.practice_mock else f"{self.ques_title} - Practice - Week -{self.week}"
    
    # def __str__(self) :
    #     return f"{self.ques_title} - Mock" if self.practice_mock else f"{self.ques_title} - Practice"


class QuestionApproach(Model):
    question = ForeignKey(CompilerQuestion, on_delete=CASCADE, null=True,blank=True)
    approach_title = CharField(max_length=255, null=True, blank=True)
    approach_intuition = TextField(null=True, blank=True)
    approach_algo = TextField(null=True, blank=True) 
    approach_complexity_analysis = TextField(null=True, blank=True) 

    def __str__(self):
        return f"{self.question.ques_title} - {self.approach_title}"


class QuestionApproachImage(Model):
    approach = ForeignKey(QuestionApproach, on_delete=CASCADE, related_name="question_approach_image")
    pic = ImageField(upload_to='approach_pictures', null=True, blank=True, verbose_name="Pic ")

    def __str__(self):
        return f"{self.approach.approach_title} - {self.pic}" 


class QuestionApproachCode(Model):
    approach = ForeignKey(QuestionApproach, on_delete=CASCADE, related_name="question_approach_code")
    language = CharField(max_length=25)
    code = TextField()

    def __str__(self):
        return f"{self.approach.approach_title} - {self.language}"
   

# class CompilerQuestionLoadTemplate(Model):
#     load_template = TextField(null=True, blank=True)   
    
#     @staticmethod
#     def get_compiler():
               
       
#         res = []
#         response = list(JdoodleSupportedLanguage.objects.all().values())
#         if response:
#             for compiler in response:
#                 choice_name = f"{compiler.get("name")}||{compiler.get("version_index")}"
#                 res.append((choice_name, choice_name))
                
#             return tuple(res)
#         else:
#             return (("No Data Set In Jdoodle Supported Language", "No Data Set In Jdoodle Supported Language"),)        

#     compiler = CharField(max_length=255, choices=get_compiler(), null=True,blank=True)
#     question = ForeignKey(CompilerQuestion, on_delete=CASCADE, null=True,blank=True)
#     course = ForeignKey(Course, on_delete=CASCADE, null=True,blank=True)
#     def __str__(self) :
#         return f"{self.question}, ID : " + f"{self.compiler}".split("||")[0]


class CompilerQuestionLoadTemplate(Model):
    load_template = TextField(null=True, blank=True)   
    
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

    compiler = CharField(max_length=255, choices=get_compiler(), null=True,blank=True)
    question = ForeignKey(CompilerQuestion, on_delete=CASCADE, null=True,blank=True)
    course = ForeignKey(Course, on_delete=CASCADE, null=True,blank=True)
    def __str__(self) :
        return f"{self.question}, ID : " + f"{self.compiler}".split("||")[0]

#new update 
class CompilerQuestionAtempt(Model):
    question = ForeignKey(CompilerQuestion, on_delete=CASCADE)
    student = ForeignKey(Student, on_delete=CASCADE,null=True,blank=True)
    instructor = ForeignKey(Instructor, on_delete=CASCADE ,null=True,blank=True)
    status = BooleanField(default=False)
    submited = BooleanField(default=False)
    time = DateTimeField(auto_now_add=True)
    attepmt_number = PositiveBigIntegerField(blank=True, null=True, default=0)
    load_template = ForeignKey(CompilerQuestionLoadTemplate, on_delete=CASCADE, null=True, blank=True)
    coding_language = CharField(max_length=255, help_text="Language", null=True,blank=True)
    student_ans = TextField(help_text="Student Code", null=True,blank=True)
    code_response_status = JSONField(null=True, blank=True, default=dict)
    code_response = TextField(help_text="Response from sphere-engine", null=True,blank=True)
    submissions_id = CharField(max_length=255, help_text="submissions ID from sphere-engine", null=True,blank=True)
    button_clicked =  CharField(max_length=11, choices=(
        ('Run', 'Run'),
        ('Submit','Submit')
    ), null=True,blank=True)
    score = PositiveBigIntegerField(null=True , blank=True, default=0)
    practic_time = DateTimeField(auto_now=True)
    # def __str__(self) :
    #     return f"{self.question}, {self.student}"
    def __str__(self) :
        if self.student:
            return f"{self.question}, {self.student.user.first_name}  {self.student.user.last_name}"
        else:
            return f"{self.question}, {self.instructor.user.first_name}  {self.instructor.user.last_name}"
    
class QuestionTimer(Model):
    exam_field =  CharField(max_length=20,choices=(
        ('Quiz', 'Quiz'),
        ('Mock', 'Mock'),
    ) , null= True ,  blank= True)
    time = TimeField()
    max_num_of_attempts = PositiveBigIntegerField(null= True ,  blank= False)
    week_pass_percent = PositiveBigIntegerField(null= True ,  blank= False)
    week = CharField(max_length=2, choices=(
        ('1','Week 1'),
        ('2','Week 2'),
        ('3','Week 3'),
        ('4','Week 4'),
        ('5','Week 5'),
        ('6','Week 6'),
        ('7','Week 7'),
        ('8','Week 8'),
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
    ),null= True ,  blank= True)
    no_of_questions = PositiveBigIntegerField(null= True ,  blank= True)
    course = ForeignKey(Course, on_delete=CASCADE, null=True,blank=True)
    def __str__(self) :
        return f"{self.exam_field} - Week {self.week}, Time-{self.time}, Max Attempts : {self.max_num_of_attempts}"
    
class CourseSubmission(Model):
    course = ForeignKey(Course, on_delete = CASCADE, related_name="submissioncourse")
    week = CharField(max_length=2, choices=(
        ('1','Week 1'),
        ('2','Week 2'),
        ('3','Week 3'),
        ('4','Week 4'),
        ('5','Week 5'),
        ('6','Week 6'),
        ('7','Week 7'),
        ('8','Week 8'),
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
    submission_topic = CharField(max_length=1000)

    def _str_(self) -> str:
        return f"{self.course.name}|{self.week}|{self.submission_topic}" 

#new update
class TaskSubmission(Model):  # Fix: Change Model to models.Model
    batch = ForeignKey(Batch, on_delete=CASCADE)
    project_topics = ForeignKey(ProjectTopic, on_delete=CASCADE, null=True, blank=True)
    submited_project = ForeignKey(ProjectName, on_delete=CASCADE, null=True, blank=True)
    student = ForeignKey(Student, on_delete=CASCADE)
    file = FileField(upload_to='Task-submission')
    created_at = DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, choices=(
    ('Submitted','Submitted'),
    ('Passed','Passed'),
    ('Failed','Failed')), default='Submitted')

    # def __str__(self) -> str:
    #     return f"Topic:- {self.project_topics.project_topic}|| Project:- {self.submited_project.project_name}|| Student:- {self.student.user.username}||(Task:-{self.status})"
    def __str__(self) -> str:
        # project topics
        project_topic = self.project_topics
        if project_topic:
            project_topic_name = project_topic.project_topic
        else:
            project_topic_name = None
        # project name
        sub_project_name = self.submited_project
        if sub_project_name:
            sub_project_name = sub_project_name.project_name
        else:
            sub_project_name = None

        # studen name
        student_name = f"{self.student.user.first_name} {self.student.user.last_name}"
        
        return f"Topic:- {project_topic_name}|| Project:- {sub_project_name}|| Student:- {student_name}||(Task:-{self.status})"


class MessageDetails(Model):
    choices=(
            ('1','Week 1'),
            ('2','Week 2'),
            ('3','Week 3'),
            ('4','Week 4'),
            ('5','Week 5'),
            ('6','Week 6'),
            ('7','Week 7'),
            ('8','Week 8'),
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
        )
    student = ForeignKey(Student, on_delete=CASCADE)
    course = ForeignKey(Course, on_delete=CASCADE)
    current_mock_unlock_week = CharField(max_length=2, choices=choices, null=True,blank=True)
    mock = BooleanField(default=False)
    current_quiz_unlock_week = CharField(max_length=2, choices=choices, null=True,blank=True)
    quiz = BooleanField(default=False)
    current_practice_unlock_week = CharField(max_length=2, choices=choices, null=True,blank=True)
    practice = BooleanField(default=False)
    title = CharField(max_length=1000, default="null")
    content = TextField(default="null")
    message_created = DateTimeField(auto_now_add=True)
    is_read = BooleanField(default=False)

    def _str_(self) -> str:
        return f"{self.user.username}||{self.message_created}" 
     
#new change
class SavePracticeCode(Model):
    question = ForeignKey(CompilerQuestion, on_delete=CASCADE)
    student = ForeignKey(Student, on_delete=CASCADE,null=True,blank=True)
    instructor = ForeignKey(Instructor, on_delete=CASCADE ,null=True,blank=True)
    compliler = ForeignKey(CompilerQuestionLoadTemplate, on_delete=CASCADE, null=True, blank=True)
    code_text = TextField()
    autosave_time = DateTimeField(auto_now=True)
    def _str_(self) -> str:
        return f"{self.user.username}||{self.question.ques_title}"


class MockResult(Model):
    attempt = models.IntegerField()
    question = ForeignKey(CompilerQuestion, on_delete=CASCADE, related_name="com_que", null=True, blank=True)
    student = ForeignKey(Student, on_delete=CASCADE, related_name="stu_for_result_mock")
    Course = ForeignKey(Course, on_delete=CASCADE, related_name="Course_mock_result")
    score = models.IntegerField()
    correct = BooleanField(default=False)
    week = models.IntegerField()
    
    def __str__(self) :
        return f"{self.student.user.first_name} {self.student.user.last_name} - {self.student.user.username} - {self.question.course.name} - week {self.question.week}"