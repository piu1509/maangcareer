from django.contrib import admin
from .models import *
from django.utils.translation import ngettext
from django import forms
from django.forms import Select


class CompilerQuestionLoadTemplateForm(forms.ModelForm):
    compiler = forms.ChoiceField(
        choices=[],  # Initially empty, will be populated dynamically
        widget=Select(attrs={'data-placeholder': 'Select a compiler...'}),
        required=False
    )

    class Meta:
        model = CompilerQuestionLoadTemplate
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['compiler'].choices = self.get_compiler_choices()

    def get_compiler_choices(self):
        url = "https://judge0-ce.p.rapidapi.com/languages"
        headers = {
            'x-rapidapi-host': "judge0-ce.p.rapidapi.com",
            'x-rapidapi-key': "4b6a677bb0msh842ae842567ba44p1808edjsn274c8f85283b"
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                choices = [(f"{compiler['name']} || {compiler['id']}", f"{compiler['name']} || {compiler['id']}") for compiler in data]
                return choices
            else:
                return [("No Data Set In Judge0 Supported Language", "No Data Set In Judge0 Supported Language")]
        except requests.exceptions.RequestException:
            return [("Error fetching data", "Error fetching data")]

    def clean_compiler(self):
        compiler = self.cleaned_data.get('compiler')
        if compiler:
            # Ensure the selected compiler exists in the current choices
            choices = dict(self.fields['compiler'].choices)
            if compiler not in choices:
                raise forms.ValidationError("Invalid compiler selection.")
        return compiler


class QuizAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'week',
        'course',
    )

    list_filter = (
        'course',
        'week',
    )

    search_fields = (
        'name',
    )
admin.site.register(Quiz, QuizAdmin)

class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = (
        'question',
        'quiz',
        'course'
    )

    def course(self,obj) -> str:
        name = obj.quiz.course.name
        return name if len(name) < 30 else f"{name[:27]}..."

    list_filter = (
        'quiz',
        'quiz__course'
    )

    search_fields = (
        'question',
    )

    actions = ['copy_questions']

    def copy_questions(self, request, queryset):
        for question in queryset:
            question.pk = None
            question.id = None
            question.question += ''
            question.save()

        self.message_user(
            request,
            ngettext(
                '%d question was successfully copied.',
                '%d questions were successfully copied.',
                len(queryset),
            ) % len(queryset),
        )

    copy_questions.short_description = "Copy selected questions"
admin.site.register(QuizQuestion, QuizQuestionAdmin)

class QuestionApproachImageInline(admin.TabularInline):
    model = QuestionApproachImage
    extra = 1  # Number of extra forms to display

class QuestionApproachCodeInline(admin.TabularInline):
    model = QuestionApproachCode
    extra = 1  # Number of extra forms to display

class QuestionApproachAdmin(admin.ModelAdmin):
    list_display = ('approach_title', 'approach_intuition')
    search_fields = ('question__ques_title',)     # Make question title searchable
    list_filter = ('question',)
    inlines = [QuestionApproachImageInline, QuestionApproachCodeInline]


class QuestionApproachInline(admin.StackedInline):
    model = QuestionApproach
    extra = 1

    # Customizing form to show inline fields
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.model = QuestionApproach
        return formset


class CompilerQuestionAdmin(admin.ModelAdmin):
    list_display = (
        'ques_title',
        'week',
        'day',
        'practice_or_mock',
        'disable',
    )

    list_filter = (
        'course',
        'practice_mock',
        'day',
        'week',
        'disable',
        'google',
        'amazon',
        'microsoft',
        'meta',
        'linkedin',
        'uber',
        'adobe',
        'cred',
    )

    search_fields = (
        'ques_title',
        'prob_text',
    )
    inlines = [QuestionApproachInline]

    actions = ['copy_questions']

    def copy_questions(self, request, queryset):
        for question in queryset:
            question.pk = None
            question.id = None
            question.ques_title += ''
            question.save()

        self.message_user(
            request,
            ngettext(
                '%d question was successfully copied.',
                '%d questions were successfully copied.',
                len(queryset),
            ) % len(queryset),
        )

    copy_questions.short_description = "Copy selected questions"
admin.site.register(CompilerQuestion, CompilerQuestionAdmin)

admin.site.register(QuestionApproach, QuestionApproachAdmin )

class CompilerQuestionLoadTemplateAdmin(admin.ModelAdmin):
    form = CompilerQuestionLoadTemplateForm
    list_display = ('question', 'compiler', 'course')
    search_fields = (
        'question__ques_title',
        'course__name'
    )
    list_filter = (
        'course',
        'question__practice_mock',
        'question__day',
        'question__week',
    )
    actions = ['copy_questions']

    def copy_questions(self, request, queryset):
        for question in queryset:
            question.pk = None
            question.id = None
            question.save()

        self.message_user(
            request,
            ngettext(
                '%d question was successfully copied.',
                '%d questions were successfully copied.',
                len(queryset),
            ) % len(queryset),
        )

    copy_questions.short_description = "Copy selected questions"

admin.site.register(CompilerQuestionLoadTemplate, CompilerQuestionLoadTemplateAdmin)

# class QuestionTimerAdmin(admin.ModelAdmin):
#     list_filter = (
#         'course__name',
#         'exam_field',
#         'week',
#     )
# admin.site.register(QuestionTimer, QuestionTimerAdmin)

class QuestionTimerAdmin(admin.ModelAdmin):
    list_filter = (
        'course__name',
        'exam_field',
        'week',
    )
    
    actions = ['copy_quiz_timers'] 

    def copy_quiz_timers(self, request, queryset): 
        for timer in queryset:
            timer.pk = None
            timer.id = None
            timer.save()

        self.message_user(
            request,
            ngettext(
                '%d timer was successfully copied.',
                '%d timers were successfully copied.',
                len(queryset),
            ) % len(queryset),
        )

    copy_quiz_timers.short_description = "Copy selected quiz timers"

admin.site.register(QuestionTimer, QuestionTimerAdmin)

class QuizAttemptAdmin(admin.ModelAdmin):
    list_filter = (
        'quiz__course__name',
        'quiz__week',
    )
        
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__user__username", 
        "quiz__course__name", 
        "quiz__week", 
    )
admin.site.register(QuizAttempt,QuizAttemptAdmin)
# admin.site.register(QuestionTimer)
# admin.site.register(CompilerQuestionLoadTemplate)
class CompilerQuestionAtemptAdmin(admin.ModelAdmin):
    list_filter = (
        'question__course__name',
        'question__week',
    )
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__user__username", 
    )
admin.site.register(CompilerQuestionAtempt,CompilerQuestionAtemptAdmin)

admin.site.register(MessageDetails)
admin.site.register(SavePracticeCode)
admin.site.register(CourseSubmission)
class MockResultAdmin(admin.ModelAdmin):
    list_filter = (
        'question__course__name',
        'question__week',
    )
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__user__username", 
        "question__course__name", 
        "question__week", 
    )
admin.site.register(MockResult,MockResultAdmin)


class TaskSubmissionAdmin(admin.ModelAdmin):
    list_filter = (
        'batch__course__name',
        'submited_project__project_name',
        'project_topics__project_topic',
    )
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__user__username", 
        "student__user__email",
    )

admin.site.register(TaskSubmission, TaskSubmissionAdmin)




