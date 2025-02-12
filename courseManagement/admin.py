from django.contrib import admin
from .models import *
from django.urls import reverse
from django.utils.html import format_html
from django.forms.models import inlineformset_factory
from django.contrib import messages
admin.site.site_header = "MAANGCareers Administration Page"
admin.site.index_title = "MAANGCareers Login"
admin.site.site_title = "MAANGCareers Admin"

def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper

class InstamentDetailsInline(admin.TabularInline):
    model = InstamentDetails
    extra = 0

# Create an inline formset for InstamentDetails within EmiDetails
InstamentDetailsFormSet = inlineformset_factory(EmiDetails, InstamentDetails, fields=['instalment', 'amount'], extra=1, can_delete=True)

class EmiDetailsInline(admin.StackedInline):
    model = EmiDetails
    extra = 0
    inlines = [InstamentDetailsInline]

    def get_formset(self, request, obj=None, **kwargs):
        # Here, you can customize the formset if necessary
        formset = super().get_formset(request, obj, **kwargs)

        class CustomInstamentDetailsFormSet(formset):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if self.instance.pk:  # Check if the instance exists
                    for form in self.forms:
                        form.instance.emi_type = self.instance

        return CustomInstamentDetailsFormSet

class lessonInline(admin.TabularInline):
    model = Topic
    extra = 0


class syllabusInline(admin.TabularInline):
    model = Week
    extra = 0


class CourseAdvantageInline(admin.TabularInline):
    model = CourseAdvantage
    extra = 0


class CourseIncludeInline(admin.TabularInline):
    model = CourseInclude
    extra = 0


class CourseCaptionInline(admin.TabularInline):
    model = CourseCaption
    extra = 0


class CourseIncludeTopicInline(admin.TabularInline):
    model = CourseIncludeTopic
    extra = 0


class batchInline(admin.StackedInline):
    model = Batch
    extra = 0

class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "discount_percentage",
        "batch",
        "archive",
        "popular",
        "premium",
        "pre_recorded"
    )
    list_editable = list_display[4:]
    search_fields = list_display[:3]
    list_filter = list_display[4:]
    inlines = [
        # batchInline,
        syllabusInline,
        EmiDetailsInline,
        CourseAdvantageInline,
        CourseIncludeInline,
        CourseIncludeTopicInline,
        CourseCaptionInline,
    ]

admin.site.register(Course, CourseAdmin)

admin.site.register(CourseTopic)

class EmiDetailsAdmin(admin.ModelAdmin):
    list_display = ('emi_type', 'instament_number', 'total_payment', 'course')
    list_filter = ('course__name',)
    search_fields = ('emi_type', 'course__name')
    inlines = [InstamentDetailsInline]

admin.site.register(EmiDetails, EmiDetailsAdmin)

class WeekAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "course",
    )
    search_fields = list_display
    list_filter = (
        'course',
    )
    inlines = [lessonInline]

admin.site.register(Week,WeekAdmin)

class TopicAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "week",
        "duration"
    )
    search_fields = list_display[:2]
    list_filter = (
        'week',
        'week__course'
    )

admin.site.register(Topic,TopicAdmin)

class TimeTableInline(admin.TabularInline):
    model = TimeTable
    extra = 0
    
class StudentInline(admin.TabularInline):
    model = BatchJoined
    extra = 0
    readonly_fields = (
        'student',
        'get_assign_project_topic',
        'payment_id',
        'full_payment_status',
        'display_full_payment_status',  # Changed field name here for display
        'total_payment'
    )

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
        
        return format_html("<br>".join(assignment_details))  # Use HTML line break for table display

    get_assign_project_topic.short_description = 'Assign Project + Topic'
    get_assign_project_topic.allow_tags = True  # Allow HTML tags to render properly in admin display

    def display_full_payment_status(self, instance):
        if instance.batch.completed:
            if instance.full_payment_status:
                return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
            else:
                return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')
        else:
            return format_html('<p style="color:red; font-size:9px;"><i> Batch not completed </i></p>')

    display_full_payment_status.short_description = 'Is Certified'  # Change the header name for display

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj=obj, **kwargs)
        exclude_fields = ['assign_topics', 'assign_projects']
        for field_name in exclude_fields:
            if field_name in formset.form.base_fields:
                del formset.form.base_fields[field_name]
        return formset

class BatchAdmin(admin.ModelAdmin):
    change_form_template = "admin/custom_change_form.html"
    list_display = (
        "name",
        "course",
        "enrolled",
        "instructor",
        "start_date",
        "end_date",
        "completed"
    )
    inlines = (TimeTableInline, StudentInline)
    search_fields = ('name',)
    list_filter = (
        ('timetable__start_date', custom_titled_filter('TimeTable Start Date')),
        'course',
        'completed',
    )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        batch = Batch.objects.filter(id=object_id)
        if batch.exists():
            batch_id = batch.first().id
        else:
            batch_id = 0
        extra_context['custom_button'] = True
        extra_context['batch_id'] = batch_id
        url = reverse('stud-project-assign', args=[batch_id])
        context = {'custom_url': url}
        extra_context.update(context)
        return super().changeform_view(request, object_id, form_url, extra_context)

admin.site.register(Batch, BatchAdmin)

class TimeTableAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "start_time",
        "start_date",
        "start_time"
    )
    search_fields = list_display[1:]
    list_filter = (
        'start_date',
        'batch__course',
        'batch',
    )

admin.site.register(TimeTable,TimeTableAdmin)

class NoteAdmin(admin.ModelAdmin):
    list_display = (
        "topic",
        "course",
        "week"
    )

    list_filter = (
        'course',
        'week'
    )

    search_fields = (
        'topic',
    )

admin.site.register(Note, NoteAdmin)
admin.site.register(ProjectName)
admin.site.register(ProjectTopic)

class BatchJoinedAdmin(admin.ModelAdmin):
    list_display = ['student', 'batch', 'full_payment_status','joined_at']
    search_fields = ['student__user__username', 'batch__id', "student__user__first_name", "student__user__last_name"]
    readonly_fields = ['get_assign_project_topic', 'get_student_emi']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('student', 'batch', 'student__user')  # Prefetch related objects
        return queryset

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
        
        return format_html("<br>".join(assignment_details))  # Use HTML line break for table display

    get_assign_project_topic.short_description = 'Assign Project + Topic'
    get_assign_project_topic.allow_tags = True  # Allow HTML tags to render properly in admin display

    def get_student_emi(self, instance):
        emi_records = StudentEmi.objects.filter(student=instance.student, batch=instance.batch)
        if not emi_records.exists():
            return "No EMI records found."

        emi_details = []
        for record in emi_records:
            emi_details.append(f"EMI {record.emi_number}: {record.amount} - Status: {'Paid' if record.payment_status else 'Unpaid'}")

        return format_html("<br>".join(emi_details))

    get_student_emi.short_description = 'Student EMI Records'

    readonly_fields = ['student', 'get_assign_project_topic', 'payment_id', 'get_student_emi']

admin.site.register(BatchJoined, BatchJoinedAdmin)

@admin.register(StudentEmi)
class StudentEmiAdmin(admin.ModelAdmin):
    list_display = ('student', 'batch', 'amount', 'emi_number', 'payment_status', 'created_at')
    list_filter = ('batch', 'payment_status')
    search_fields = ('batch_id', 'student__user__username', "student__user__first_name", "student__user__last_name")
    autocomplete_fields = ('batch', 'student')

    def save_model(self, request, obj, form, change):
        try:
            obj.update_total_payment()
        except ValidationError as e:
            messages.error(request, f"Error: {e}")
            return
        super().save_model(request, obj, form, change)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
admin.site.register(EmiReminderStatusLog)