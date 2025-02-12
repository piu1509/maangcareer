from django.contrib import admin
from .models import *
from courseManagement.models import *
from freeCourseManagement.helpers import *
from concurrent.futures import ThreadPoolExecutor
from courseManagement.helpers import send_email_for_payment_clear
# Register your models here.

admin.site.register(Syllabus)


class BatchCompleteRequestAdmin(admin.ModelAdmin):
    list_display = ('batch', 'instructor', 'request_date', 'is_complete',)
    list_filter = ('is_complete',)
    search_fields = ('batch__id', 'instructor__user__username',)

    def send_emails_in_background(self, batch_id):
        batch = Batch.objects.get(id=batch_id)
        student_ids = batch.students.values_list('id', flat=True)
        subject = "Release certificate"

        for student_id in student_ids:
            email = Student.objects.get(id=student_id).user.email
            payment_status = BatchJoined.objects.filter(batch=batch, student_id=student_id).first().full_payment_status
            if payment_status:
                download_link = "https://dev.maangcareers.in/student/certificates"
                message = "Your course is completed, please collect the certificate"
                email_status = send_email_for_certificate(download_link, email, batch.course.name)
            else:
                download_link = "https://dev.maangcareers.in/student/certificates"
                message = "Your course is completed, your payment is not clear"
                email_status = send_email_for_payment_clear(download_link, email, batch.course.name)
            
            print(email_status)

    def save_model(self, request, obj, form, change):
        if obj.is_complete == "approved":
            batch = obj.batch            

            try:              
                batch.completed = True
                
                batch.b_certificate = True
                batch.save()

                if obj.send_email_for_certification:
                    # Use a ThreadPoolExecutor to send emails in the background
                    with ThreadPoolExecutor() as executor:
                        executor.submit(self.send_emails_in_background, batch.id)

            except TimeTable.DoesNotExist:
                # Handle the case where no timetable entry exists
                pass
         
        if obj.is_complete in ["rejected", "pending"]:
            try:
                batch = obj.batch
                batch.completed = False
                batch.end_date = None
                batch.revoke_date = None
                batch.b_certificate = True
                batch.save()
            except:
                pass
         
        super().save_model(request, obj, form, change)

admin.site.register(BatchCompleteRequest, BatchCompleteRequestAdmin)