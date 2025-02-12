from django.contrib import admin
from freeCourseManagement.models import *
from django.utils.translation import ngettext
from django import forms
from django.forms import Select
from django.http import JsonResponse
from django.urls import path

# Register your models here.

class FreeCourseAdvantageInline(admin.TabularInline):
    model = FreeCourseAdvantage
    extra = 0


class FreeCourseIncludeInline(admin.TabularInline):
    model = FreeCourseInclude
    extra = 0


class FreeCourseIncludeTopicInline(admin.TabularInline):
    model = FreeCourseIncludeTopic
    extra = 0

class FreeCourseCaptionInline(admin.TabularInline):
    model = FreeCourseCaption
    extra = 0

class FreeCourseAdmin(admin.ModelAdmin):
    list_display = (
        "name",  
        "section_number",      
        "archive",
        "popular",       
        "pre_recorded"
    )
    search_fields = list_display
    list_filter = list_display
    inlines = [
        FreeCourseAdvantageInline,
        FreeCourseIncludeInline,
        FreeCourseIncludeTopicInline,
        FreeCourseCaptionInline,
        
    ]
    actions = ['copy_course']

    def copy_course(self, request, queryset):
        for course in queryset:
            course.pk = None
            course.id = None
            course.name += ''
            course.save()

        self.message_user(
            request,
            ngettext(
                '%d course was successfully copied.',
                '%d courses were successfully copied.',
                len(queryset),
            ) % len(queryset),
        )

    copy_course.short_description = "Copy selected courses"

admin.site.register(FreeCourse, FreeCourseAdmin)


class SyllabusTopicsInline(admin.TabularInline):
    model = SyllabusTopics
    extra = 0

class FreeCourseSyllabusAdmin(admin.ModelAdmin):
    autocomplete_fields = ['course']
    readonly_fields = ('number',)
    list_display = (
        "course",
        "number",
        "name",
        "max_attempts",
        "max_score",
        "max_attempts_mock",
        "max_score_mock" ,
    )
    search_fields = list_display
    list_filter = list_display
    inlines = [
        SyllabusTopicsInline,
        
    ]
admin.site.register(FreeCourseSyllabus, FreeCourseSyllabusAdmin)

######

class QuizQuestionInline(admin.TabularInline):
    model = FreeCourseQuizQuestion
    extra = 0


class CourseSectionQuestionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['course_section']
    inlines = [
        QuizQuestionInline,        
    ]
admin.site.register(CourseSectionQuestion, CourseSectionQuestionAdmin)


####
class FreeCourseJoineeAdmin(admin.ModelAdmin):
    autocomplete_fields = ['course', 'student']
    list_display = (
        "course", 
        "student"       
    )
    search_fields = list_display
    list_filter = list_display

admin.site.register(FreeCourseJoinee, FreeCourseJoineeAdmin)
admin.site.register(QuizQuestionAttempts)

class SyllabusTopicsAdmin(admin.ModelAdmin):
    list_display = ('title', 'section')  # Adjust as needed
    search_fields = ('title', 'section__name')  # Adjust as needed

admin.site.register(SyllabusTopics, SyllabusTopicsAdmin)

### Compiler question part

class FreeCourseCompilerQuestionApproachImageInline(admin.TabularInline):
    model = FreeCourseCompilerQuestionApproachImage
    extra = 0  # Number of extra forms to display


class FreeCourseCompilerQuestionApproachCodeInline(admin.TabularInline):
    model = FreeCourseCompilerQuestionApproachCode
    extra = 0  # Number of extra forms to display


class FreeCourseCompilerQuestionApproachAdmin(admin.ModelAdmin):
    list_display = ('approach_title', 'approach_intuition')
    search_fields = ('question__ques_title',)     # Make question title searchable
    list_filter = ('question', 'question__course_section', 'question__course_section__course')
    inlines = [FreeCourseCompilerQuestionApproachImageInline, FreeCourseCompilerQuestionApproachCodeInline]


class FreeCourseCompilerQuestionExampleImageInline(admin.TabularInline):
    model = FreeCourseCompilerQuestionExampleImage
    extra = 0


class FreeCourseCompilerQuestionApproachInline(admin.TabularInline):
    model = FreeCourseCompilerQuestionApproach
    extra = 0

    # Customizing form to show inline fields
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.model = FreeCourseCompilerQuestionApproach
        return formset

class FreeCourseCompilerQuestionLoadTemplateInline(admin.TabularInline):
    model = FreeCourseCompilerQuestionLoadTemplate
    extra = 0


class FreeCourseCompilerQuestionAdmin(admin.ModelAdmin):

    autocomplete_fields = ['course_section', 'topic']
    list_display = (
        'ques_title',
        'practice_mock',
        'disable',
    )

    list_filter = (
        'course_section',
        'topic',
        'practice_mock',
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
    inlines = [FreeCourseCompilerQuestionExampleImageInline, FreeCourseCompilerQuestionApproachInline, FreeCourseCompilerQuestionLoadTemplateInline]

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

    
admin.site.register(FreeCourseCompilerQuestion, FreeCourseCompilerQuestionAdmin)
admin.site.register(FreeCourseCompilerQuestionApproach, FreeCourseCompilerQuestionApproachAdmin )



class FreeCourseCompilerQuestionAttemptAdmin(admin.ModelAdmin):
    autocomplete_fields = ['question', 'student']
    list_filter = (
        'question__ques_title',
        'question__practice_mock',
        'question__course_section__name'
    )
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__user__username", 
    )
admin.site.register(FreeCourseCompilerQuestionAttempt,FreeCourseCompilerQuestionAttemptAdmin)

admin.site.register(SavePracticeCompilerQuestionCode)
admin.site.register(MockCompilerQuestionResult)