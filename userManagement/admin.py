from typing import Any, List, Tuple
from django.contrib import admin
from django.db.models.query import QuerySet
from .models import *
from testsManagement.models import Quiz
from django.contrib.admin import SimpleListFilter
from datetime import date
from testsManagement.models import *
from django import forms
from freeCourseManagement.models import *

class EnrolledListFilter(SimpleListFilter):
    title = 'Currenty Enrolled'
    parameter_name = 'enroled'
    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
        return (
            ('true','Enrolled'),
            ('false','Not Enrolled')
        )
    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == 'true':return queryset.filter(batches__end_date__gte = date.today())
        elif self.value() == 'false':return queryset.filter(batches__end_date__lt = date.today())
        return queryset

class BatchInline(admin.TabularInline):
    model = Student.batches.through
    extra = 0

class QuizAttempInline(admin.TabularInline):
    model = Quiz.students.through
    extra = 0
    # exclude = ('answers',)
    fields = [ "quiz","attempts","score","passed"]
    readonly_fields = ("quiz","attempts","score","passed")

class MockResultInline(admin.TabularInline):
    model = MockResult
    fields=("question","attempt","score","correct")
    readonly_fields = ("question", "attempt", "score", "correct")
    extra = 0    
    # exclude = ('Course',)

class CompilerQuestionAtemptInline(admin.TabularInline):
    model = CompilerQuestionAtempt
    fields=("question","status","submited","submissions_id")
    readonly_fields = ("question","status","submited","submissions_id")
    extra = 0 

class FreeCourseQuizAttemptInline(admin.TabularInline):
    model = QuizQuestionAttempts
    fields = ("course", "syllabus", "attempt_number","attempt_answer", "attempt_score","is_passed","right_answers","wrong_answers")
    readonly_fields = ("course", "syllabus", "attempt_number","attempt_answer", "attempt_score","is_passed","right_answers","wrong_answers")
    extra = 0

class FreeCoursePracticeAttemptsInline(admin.TabularInline):
    model = FreeCourseCompilerQuestionAttempt
    fields = ("question","course","syllabus","attepmt_number", "submitted","status","code_response_status")
    readonly_fields = ("question","course","syllabus","attepmt_number", "submitted","status","code_response_status")
    extra = 0

class FreeCourseMockAttemptsInline(admin.TabularInline):
    model = MockCompilerQuestionResult
    fields = ("course", "course_section", "questions", "attempt_number", "score", "is_passed", "right_answers", "wrong_answers")
    readonly_fields = ("course", "course_section", "questions", "attempt_number", "score", "is_passed", "right_answers", "wrong_answers")
    extra = 0

class StudentPersonalDetailsInline(admin.TabularInline):
    model = StudentPersonalDetails
    fields = ("location", "university","role")
    extra= 0 

class StudentAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'phone_num',
        'user_email',
        'latest_batch',
        'joined_date',
    )
    def user_email(self, obj) -> str:return obj.user.email
    def latest_batch(self, obj) -> str: return obj.batches.last()
    inlines = (
        StudentPersonalDetailsInline,
        BatchInline,
        QuizAttempInline,
        MockResultInline,
        CompilerQuestionAtemptInline,
        FreeCourseQuizAttemptInline,
        FreeCoursePracticeAttemptsInline, 
        FreeCourseMockAttemptsInline
    )
    search_fields = (
        'user__first_name',
        'user__last_name',
        'user__email',
    )
    list_filter = (
        'joined_date',
        EnrolledListFilter,
    )
admin.site.register(Student, StudentAdmin)

class InstructorAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'phone_num',
        'joined_date',
        'present_company'
    )
    search_fields = (
        'user__first_name',
        'user__last_name'
        'present_company'
    )
admin.site.register(Instructor, InstructorAdmin)

class salesPersonAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'phone_num',
    )
    search_fields = (
        'user__first_name',
        'user__last_name'
    )
admin.site.register(SalesPerson, salesPersonAdmin)


class SubAdminAdmin(admin.ModelAdmin):
    
    list_display = ['user','phone_num','photo','location']

admin.site.register(SubAdmin, SubAdminAdmin)

class DataEntryUserAdmin(admin.ModelAdmin):
    
    list_display = ['user','phone_num','photo','location']

admin.site.register(DataEntryUser, DataEntryUserAdmin)


class LeaveRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'type','num_of_days', 'from_date', 'to_date', 'status']
    search_fields = ['user', 'user_type', 'type','num_of_days', 'from_date', 'to_date', 'status']
    autocomplete_fields = ['user']


admin.site.register(LeaveRecord, LeaveRecordAdmin)

class ExpenseInline(admin.TabularInline):  # Or use admin.StackedInline for a different layout
    model = Expense
    extra = 0  # Number of extra blank Expense forms to display

# Define the admin for ExpenseType, showing the related Expense models inline
class ExpenseTypeAdmin(admin.ModelAdmin):
    inlines = [ExpenseInline]
    list_display = ('type',)
    search_fields = ('type',)

admin.site.register(ExpenseType, ExpenseTypeAdmin)