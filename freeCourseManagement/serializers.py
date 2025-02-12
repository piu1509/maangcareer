from .models import *

from rest_framework.serializers import ModelSerializer, SerializerMethodField, StringRelatedField, CharField

class FreeCourseAdvantageSerializer(ModelSerializer):
    class Meta:
        model = FreeCourseAdvantage
        fields = ("point",)
        depth = 1

class FreeCourseIncludeSerializer(ModelSerializer):
    class Meta:
        model = FreeCourseInclude
        fields = ("include",)
        depth = 1

class FreeCourseIncludeTopicSerializer(ModelSerializer):
    class Meta:
        model = FreeCourseIncludeTopic
        fields = ("topic",)
        depth = 1

class FreeCourseCaptionSerializer(ModelSerializer):
    class Meta:
        model = FreeCourseCaption
        fields = ("caption",)
        depth = 1

class SyllabusTopicsSerializer(ModelSerializer):
    class Meta:
        model = SyllabusTopics
        fields = "__all__"
        depth = 1

class FreeCourseSyllabusSerializer(ModelSerializer):
    syllabus_topics = SyllabusTopicsSerializer(many=True, read_only=True)
    class Meta:
        model = FreeCourseSyllabus
        fields = (
            "id",
            "number",
            "name",
            "syllabus_topics"
        )
        depth = 1

    def get_syllabus_topics(self, obj):
        topics = SyllabusTopics.objects.filter(section=obj).order_by('number')
        return TopicWithQuestionsSerializer(topics, many=True).data


class FreeCourseSerializer(ModelSerializer):
    free_course_advantages = FreeCourseAdvantageSerializer(many=True, read_only=True)
    free_course_includes = FreeCourseIncludeSerializer(many=True, read_only=True)
    free_course_topics = FreeCourseIncludeTopicSerializer(many=True, read_only=True)
    free_course_caption = FreeCourseCaptionSerializer(many=True, read_only=True)
    course_syllabus = FreeCourseSyllabusSerializer(many=True, read_only=True)
    is_registered = SerializerMethodField()

    class Meta:
        model = FreeCourse
        fields = (
            "id",
            "serial_no",
            "author_message",
            "author_name",
            "author_photo",
            "caption",
            "certificate",
            "demo_video",
            "description",                       
            "mobile_computer",            
            "name",
            "popular",
            "pre_recorded",            
            "projects",
            "requirements",
            "short_description",
            "thumbnail",            
            "free_course_advantages",
            "free_course_includes",
            "free_course_topics",
            "free_course_caption",
            "is_registered",
            "course_syllabus",
            "certificate_no"
            
        )
    def get_is_registered(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'student'):  # Check if user is authenticated and is a student
            check_freecourse_joinee = FreeCourseJoinee.objects.filter(course=obj, student=request.user.student)
            return check_freecourse_joinee.exists()
        return False
        
    def to_representation(self, instance):
        
        ret = super().to_representation(instance)
        ret['course_syllabus'] = sorted(
            ret['course_syllabus'], key=lambda x: x['number']
        )
        return ret


class FreeCourseListSerializer(ModelSerializer):
    class Meta:
        model = FreeCourse
        fields = (
            "id", 
            "serial_no" ,          
            "name",
            "popular",            
            "projects",
            "short_description",
            "thumbnail",            
        )


class QuizQuestionSerializer(ModelSerializer):
    topic = StringRelatedField(source='topic.title')
    class Meta:
        model = FreeCourseQuizQuestion    
        fields = ("id","course_section_question","topic", "question", "option1", "option2", "option3", "option4", "answer")



### compiler part

class SyllabusLockSerializer(ModelSerializer):
    class Meta:
        model = FreeCourseSyllabus
        fields = [
            "id",
            "number",
            "name",
            "max_score_practice"
            ]


class SyllabusLockStatusSerializer(ModelSerializer):
    class Meta:
        model = FreeCourseSyllabus
        fields = [
            "id",
            "number",
            "name",
            "max_attempts_mock",
            "max_score_mock",
            "time_duration_mock"
            ]

class CourseSectionQuestionSerializer(ModelSerializer):
    quiz_questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = CourseSectionQuestion
        fields = '__all__'

class QuestionApproachCodeSerializer(ModelSerializer):
    class Meta:
        model = FreeCourseCompilerQuestionApproachCode
        fields = ['id', 'language', 'code']

class QuestionApproachImageSerializer(ModelSerializer):
    class Meta:
        model = FreeCourseCompilerQuestionApproachImage
        fields = ['id', 'pic']

class QuestionApproachSerializer(ModelSerializer):
    free_question_approach_image = QuestionApproachImageSerializer(many=True, read_only=True)
    free_question_approach_code = QuestionApproachCodeSerializer(many=True, read_only=True)

    class Meta:
        model = FreeCourseCompilerQuestionApproach
        fields = ['id', 'approach_title', 'approach_intuition', 'approach_algo', 'approach_complexity_analysis', 'free_question_approach_image', 'free_question_approach_code']

class ExampleImageSerializer(ModelSerializer):
    name = SerializerMethodField()
    class Meta:
        model = FreeCourseCompilerQuestionExampleImage
        fields = ["id", "name","example_picture"]

    def get_name(self, obj):
        return obj.example_name if obj.example_name else None


class FreeCourseCompilerQuestionSerializer(ModelSerializer):
    free_course_compiler_question_approach = QuestionApproachSerializer(many=True, read_only=True)
    free_course_com_ques_ex_image = ExampleImageSerializer(many=True, read_only=True)
    video_solutions = SerializerMethodField()
    test_cases = SerializerMethodField()
    examples = SerializerMethodField()
    constraints = SerializerMethodField()

    class Meta:
        model = FreeCourseCompilerQuestion
        fields = ['id', 'practice_mock', 'question_number', 'ques_title', 'google', 'amazon', 'microsoft', 'meta', 'linkedin', 'uber', 'adobe', 'cred',
                  'prob_text', 'prob_pic', 'examples','free_course_com_ques_ex_image', 'constraints', 'const_pic', 'challenge', 'video_solutions', 'test_cases',
                  'free_course_compiler_question_approach']
        
    def get_video_solutions(self, obj):
        all_videos = []
        if obj.video_solutions is not None and len(obj.video_solutions) != 0:
            try:
                vids = str(obj.video_solutions).split("\r\n\r\n\r\n")
                for v in vids:
                    vidd = str(v).replace("\r", "").replace("\n", "")
                    nw_vids = vidd.split("||")
                    vid_language = nw_vids[0]
                    vid_url = nw_vids[1]
                    all_videos.append({"video_title": vid_language, "video_links": vid_url})
            except:
                all_videos.append({
                    "info": "Please follow The Process"
                })
        return all_videos
    
    def get_examples(self, obj):
        examples = []
        if obj.examples is not None and len(obj.examples) != 0:
            try:
                exs = str(obj.examples).split("\r\n\r\n\r\n")
                example_id = 1  

                for i in exs:
                    ex = str(i).replace("\r", "").replace("\n", "")
                    ex_ = ex.split('||')

                    title = ex_[0] if len(ex_) > 0 else ""
                    input = ex_[1] if len(ex_) > 1 else ""
                    output = ex_[2] if len(ex_) > 2 else ""
                    explanation = ex_[3] if len(ex_) > 3 else ""

                    examples.append({
                        "id": example_id, 
                        "title": title, 
                        "input": input, 
                        "output": output, 
                        "explanation": explanation
                    })
                    example_id += 1
            except:
                examples.append({
                    "info": "Please follow The Process"
                })
        return examples

    def get_constraints(self, obj):
        constraints = []
        if obj.constraints is not None and len(obj.constraints) != 0:
            try:
                cons = str(obj.constraints).split("\r\n\r\n\r\n")                 

                for i in cons:
                    ex = str(i).replace("\r", "").replace("\n", "")
                    ex_ = ex.split('||')

                    constrain_title = ex_[0] if len(ex_) > 0 else ""
                    constrain_value = ex_[1] if len(ex_) > 1 else ""                    

                    constraints.append({
                        "constrain_title": constrain_title, 
                        "constrain_value": constrain_value                        
                    })
                    
            except:
                constraints.append({
                    "info": "Please follow The Process"
                })
        return constraints

    
    def get_test_cases(self, obj):
        return obj.test_cases_to_view

class TopicWithQuestionsSerializer(ModelSerializer):  
    topic =  CharField() 
    questions = FreeCourseCompilerQuestionSerializer(many=True)

    class Meta:
        model = SyllabusTopics
        fields = ['topic', 'questions']


class CompilerQuestionLoadTemplateSerializer(ModelSerializer):
    class Meta:
        model = FreeCourseCompilerQuestionLoadTemplate
        fields = ['id', 'load_template', 'compiler']

 