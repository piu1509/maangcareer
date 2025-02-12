
from courseManagement.models import *
from rest_framework import serializers
from testsManagement.models import *
from freeCourseManagement.models import *
from django.contrib.auth.models import User

class CustomCourseSerializer(serializers.ModelSerializer):
    batch_complemted = serializers.SerializerMethodField()
    batch_ongoing = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (           
            
            "id",            
            "name",
            "course_duration_in_months",                
            "batch_complemted",
            "batch_ongoing",
            "role"
                       
        )
    def get_batch_complemted(self, obj):
        # Count the completed batches for this course
        return obj.batches.filter(completed=True).count()

    def get_batch_ongoing(self, obj):
        # Count the ongoing (not completed) batches for this course
        return obj.batches.filter(completed=False).count()


class BatchCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "name"
        ) 


class ProjectNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectName
        fields = ['id', 'project_name']


class ProjectTopicSerializer(serializers.ModelSerializer):
    project_name = ProjectNameSerializer(many=True)  

    class Meta:
        model = ProjectTopic
        fields = ['id', 'project_topic', 'project_name'] 


class InstructorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Assuming you want to show the username of the related User

    class Meta:
        model = Instructor
        fields = (
            'id',
            'user',
        )


class TimeTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeTable
        fields = (
            "id",
            "topic",
            "start_date",
            "start_time",
            "end_time",
            "link",
            "week",
            "day"

        )


class StudentListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    class Meta:
        model = Student
        fields = (
            "id",
            "name",
            "email",
            "phone_num",
        )
    def get_name(self, obj):
        name = f'{obj.user.first_name} {obj.user.last_name}'
        return name
    def get_email(self, obj):
        return obj.user.email


class BatchJoinedSerializer(serializers.ModelSerializer):
    student = StudentListSerializer()
    assign_project_topic = serializers.SerializerMethodField()
    student_emi_records = serializers.SerializerMethodField()

    class Meta:
        model = BatchJoined
        fields = [
            'student',  
            'payment_id', 
            'full_payment_status', 
            'choice_emi_type', 
            'total_payment',  
            'assign_project_topic', 
            'student_emi_records'
        ]
        depth = 1  # To include related data for student and batch

    def get_assign_project_topic(self, instance):
        topics = instance.assign_topics.all()
        projects = instance.assign_projects.all()
        assignment_details = []

        for idx, topic in enumerate(topics, start=1):
            project = projects.filter(projecttopic=topic).first()  # Get the project for the specific topic
            if project:
                assignment_details.append(f"{idx}. {topic.project_topic} :- {project.project_name}")

        if not assignment_details:
            return "NA"
        
        return assignment_details

    def get_student_emi_records(self, instance):
        emi_records = StudentEmi.objects.filter(student=instance.student, batch=instance.batch)
        if not emi_records.exists():
            return "No EMI records found."

        emi_details = []
        for record in emi_records:
            emi_details.append({
                "emi_number": record.emi_number,
                "amount": record.amount,
                "status": "Paid" if record.payment_status else "Unpaid"
            })

        return emi_details


class BatchDetailsSerializer(serializers.ModelSerializer):
    course = BatchCourseSerializer()
    project_topics = ProjectTopicSerializer(many=True)
    instructor = InstructorSerializer()    

    class Meta:
        model = Batch
        fields = (
            "id",
            "name",
            "course",
            "project_topics",
            "max_participants",
            "start_date",
            "end_date",
            "completed",
            "link",
            "revoke_date",
            "b_certificate",
            "revoke_days",
            "instructor",          

        )



class CustomBatchSerializer(serializers.ModelSerializer):
    course = CustomCourseSerializer()
    class Meta:
        model = Batch
        fields = (
            "id",
            "name",
            "course",
            "instructor",
            "enrolled",
            "start_date",
            "end_date",
            "completed"
        )


class StudentSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    batches = CustomBatchSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = (
            "id",
            "name",
            "email",
            "phone_num",            
            "batches",
            "joined_date"
        )
    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.username
    
    def get_email(self, obj):
        return obj.user.email
    

class StudentPersonalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPersonalDetails
        fields = ('location', 'university', 'role')


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ('id', 'name')  


class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ('id', 'question', 'answers')  # Adjust as needed


class QuizSerializer(serializers.ModelSerializer):
    course_name = serializers.StringRelatedField()
    class Meta:
        model = Quiz
        fields = ('id', 'name', 'course','course_name', 'week')


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer()    
    questions = QuizQuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ('id', 'quiz', 'questions', 'passed', 'score', 'date', 'answers', 'attempts')


class CompilerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompilerQuestion
        fields = ('id', 'question_number', 'ques_title', 'week', 'day')


class MockResultSerializer(serializers.ModelSerializer):
    question = CompilerQuestionSerializer()
    class Meta:
        model = MockResult
        fields = ('question', 'attempt', 'score', 'correct')


class CompilerQuestionAtemptSerializer(serializers.ModelSerializer):
    question = CompilerQuestionSerializer()
    class Meta:
        model = CompilerQuestionAtempt
        fields = ('question', 'status', 'submited', 'submissions_id')


class StudentDetailsSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    latest_batch = serializers.SerializerMethodField()
    personal_details = StudentPersonalDetailsSerializer(source='studentDetail', many=False)    
    

    class Meta:
        model = Student
        fields = (
            'id',
            '__str__', 
            'phone_num', 
            'user_email', 
            'latest_batch', 
            'joined_date',
            'personal_details',  
            'terms_condition'          
            
        )
    
    def get_latest_batch(self, obj):
        return obj.batches.last().name if obj.batches.exists() else None


class StudentBatchJoinedSerializer(serializers.ModelSerializer):
    batch = BatchSerializer()
    assign_project_topic = serializers.SerializerMethodField()
    student_emi_records = serializers.SerializerMethodField()

    class Meta:
        model = BatchJoined
        fields = [
            'batch',  
            'payment_id', 
            'full_payment_status', 
            'choice_emi_type', 
            'total_payment',  
            'assign_project_topic', 
            'student_emi_records'
        ]
        depth = 1  # To include related data for student and batch

    def get_assign_project_topic(self, instance):
        topics = instance.assign_topics.all()
        projects = instance.assign_projects.all()
        assignment_details = []

        for idx, topic in enumerate(topics, start=1):
            project = projects.filter(projecttopic=topic).first()  # Get the project for the specific topic
            if project:
                assignment_details.append(f"{idx}. {topic.project_topic} :- {project.project_name}")

        if not assignment_details:
            return "NA"
        
        return assignment_details

    def get_student_emi_records(self, instance):
        emi_records = StudentEmi.objects.filter(student=instance.student, batch=instance.batch)
        if not emi_records.exists():
            return "No EMI records found."

        emi_details = []
        for record in emi_records:
            emi_details.append({
                "emi_number": record.emi_number,
                "amount": record.amount,
                "status": "Paid" if record.payment_status else "Unpaid"
            })

        return emi_details


class QuizQuestionAttemptsSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    syllabus_name = serializers.CharField(source='syllabus.name', read_only=True)
    syllabus_number = serializers.IntegerField(source='syllabus.number', read_only=True)
    

    class Meta:
        model = QuizQuestionAttempts
        fields = [
            'id',
            'course',
            'course_name',  
            'syllabus',
            "syllabus_name",
            'syllabus_number',            
            'attempt_number',
            'attempt_answer',
            'attempt_score',
            'is_passed',
            'attempted_at',
            'right_answers',
            'wrong_answers',
        ]
        read_only_fields = ['attempted_at']


class FreecourseCompilerQuestionSerializer(serializers.ModelSerializer):
    course_section = serializers.StringRelatedField()
    topic = serializers.StringRelatedField()
    class Meta:
        model = FreeCourseCompilerQuestion
        fields = ('id','course_section','topic', 'question_number', 'ques_title')


class FreeCoursePracticeQuestionAttemtSerializer(serializers.ModelSerializer):
    question = FreecourseCompilerQuestionSerializer()
    course = serializers.StringRelatedField()
    syllabus = serializers.StringRelatedField()
    class Meta:
        model = FreeCourseCompilerQuestionAttempt
        fields = ('id','question','course', 'syllabus', 'status','submitted','attepmt_number','code_response_status')


class FreeCourseMockAttemptSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField()
    course_section = serializers.StringRelatedField()
    questions = serializers.JSONField()  
    class Meta:
        model = MockCompilerQuestionResult
        fields = ('id', 'course', 'course_section','questions', 'attempt_number','score', 'is_passed', 'right_answers', 'wrong_answers')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username')


class FreeCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeCourse
        fields = ('id', 'name')


class FreeCourseJoineeSerializer(serializers.ModelSerializer):
    course = FreeCourseSerializer()
    class Meta:
        model = FreeCourseJoinee
        fields = ('id', 'course', 'joined_at', 'is_completed', 'is_certificate','end_date')


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username', 'email', 'first_name', 'last_name')

class LeaveRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRecord
        fields = ('id', 'type', 'reason', 'num_of_days', 'from_date', 'to_date', 'created_at', 'status', 'status_description')

class LeaveRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRecord
        fields = ('type', 'reason', 'num_of_days', 'from_date', 'to_date')

    def create(self, validated_data):
        return LeaveRecord.objects.create(**validated_data)

class SalesPersonSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()
    user = CustomUserSerializer()

    class Meta:
        model = SalesPerson
        fields = ['id','user', 'email','gender', 'phone_num', 'location', 'state', 'city','area', 'branch', 'user_type','current_salary']

    def get_user_type(self, obj):
        return 'Sales Person'


class DataEntryUserSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()
    user = CustomUserSerializer()
    class Meta:
        model = DataEntryUser
        fields = ('id', 'user','user_type', 'phone_num', 'location', 'photo', 'gender','current_salary')

    def get_user_type(self, obj):
        return 'Data Entry User'


class MentorSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()
    user = CustomUserSerializer()
    class Meta:
        model = Instructor
        fields = ('id', 'user','user_type','phone_num','location','present_company','resume','photo','terms_condition','rules_regulation_count','page_visit_count','joined_date','signature', 'gender', 'current_salary')

    def get_user_type(self, obj):
        return 'Mentor'


class ExpenseSerializer(serializers.ModelSerializer):
    from_user = serializers.StringRelatedField()

    class Meta:
        model = Expense
        fields = ('id','amount','date_time','status','receipt','transaction_no','to_user_type','from_user','transaction_mode') 

class CustomExpenseSerializer(serializers.ModelSerializer):
    from_user = serializers.StringRelatedField()
    to_user = serializers.StringRelatedField()

    class Meta:
        model = Expense
        fields = ('id','amount','date_time','status','receipt','transaction_no','to_user_type','from_user','to_user','to_user_type','transaction_mode') 

class ExpenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseType
        fields = ['id', 'type']

