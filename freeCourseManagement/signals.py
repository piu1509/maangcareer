from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FreeCourseJoinee
from freeCourseManagement.helpers import save_pdf_to_model, send_email_for_certificate


# @receiver(post_save, sender=FreeCourseJoinee)
# def handle_certificate_update(sender, instance, **kwargs):

#     if instance.is_certificate:
#         print("Certificate status updated to True")
        
#         post_save.disconnect(handle_certificate_update, sender=FreeCourseJoinee)

#         request = kwargs.get('request')  
#         download_link = save_pdf_to_model(instance.student.id, instance.course.id, request) 

#         if download_link:
#             instance.certificate = download_link
#             instance.save(update_fields=['certificate'])
        
#         post_save.connect(handle_certificate_update, sender=FreeCourseJoinee)

#         subject = 'Course Completion Certificate'
#         message = f'You have successfully completed your {instance.course.name}.'
#         send_email_for_certificate(download_link, instance.student.user.email, message, subject)
#     else:
#         print('is_certificate is False')

