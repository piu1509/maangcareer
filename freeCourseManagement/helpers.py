from .models import *
from django.db.models import Max
from django.core.mail import send_mail

import os
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.core.files.base import ContentFile
from notificationManagement.models import *
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.conf import settings
# from weasyprint import HTML

def notify_user(user_id, title, message):
    print('This function hittttttttt')
    user = User.objects.filter(id=user_id).first()
    room, created = Room.objects.get_or_create(user=user)
    notification_exists = NotificationBox.objects.filter(
        room=room, 
        notify_for=user, 
        title=title, 
        content=message
    ).exists()

    if not notification_exists:
        
        NotificationBox.objects.create(
            room=room, 
            notify_for=user, 
            title=title, 
            content=message
        )
        return True    

def check_certificate_status(course_id, student_id):
    course = FreeCourse.objects.filter(id=course_id).first()
    syllabus_list = FreeCourseSyllabus.objects.filter(course=course).values("id")
    
    certificate_status = True  
    quiz_score = []  
    mock_score = []
    practice_score = []
    for syllabus in syllabus_list:
       
        check_quiz_score = QuizQuestionAttempts.objects.filter(course_id=course_id, syllabus_id=syllabus["id"], student_id=student_id)
        total_practice_question = FreeCourseCompilerQuestion.objects.filter(course_section_id=syllabus["id"], practice_mock=False, disable=False)
        check_right_prac_ans = FreeCourseCompilerQuestionAttempt.objects.filter(course_id=course_id, syllabus_id=syllabus["id"], question__practice_mock=False, student_id=student_id, status=True)
        check_mock_score = MockCompilerQuestionResult.objects.filter(course_id=course_id, course_section_id=syllabus["id"], student_id=student_id)
        if check_quiz_score and check_right_prac_ans and check_mock_score:
            get_quiz_score = check_quiz_score.aggregate(max_score=Max('attempt_score'))['max_score']
            quiz_score.append(get_quiz_score)
            get_mock_score = check_mock_score.aggregate(max_score=Max('score'))['max_score']
            mock_score.append(get_mock_score)
            get_practice_score = (check_right_prac_ans.count() / total_practice_question.count()) * 100
            practice_score.append(get_practice_score)
    av_quiz_score = sum(quiz_score) / len(quiz_score)
    av_prac_score = sum(practice_score) / len(practice_score)
    av_mock_score = sum(mock_score) / len(mock_score)
    
    if av_quiz_score < course.average_quiz_score or av_prac_score < course.average_practice_score or av_mock_score < course.average_mock_score:
        certificate_status = False            
    
    return certificate_status


def save_pdf_to_model(student_id, course_id, end_date, request):
    student = Student.objects.get(id=student_id).user
    student_name = f"{student.first_name} {student.last_name}"
    print(student_name)
    course = FreeCourse.objects.get(id=course_id).name
    file_name = f'{student}_{course}_certificate.pdf'
    
    template = get_template('certificate/certificate_fast_track.html')
    context = {"student_name": student_name, "course_name": course, "end_date":end_date}
    html_content = template.render(context)

    buffer = BytesIO()
    pisa.CreatePDF(BytesIO(html_content.encode("UTF-8")), buffer)
    
    buffer.seek(0)
    pdf_content = buffer.read()
    buffer.close()
    
    joined_student = FreeCourseJoinee.objects.filter(course_id=course_id, student_id=student_id, is_certificate=True).first()
    if joined_student:
        joined_student.certificate.save(file_name, ContentFile(pdf_content))
        joined_student.save()


    if joined_student and joined_student.certificate:
        download_link = request.build_absolute_uri(joined_student.certificate.url)
    else:
        download_link = None
    
    return download_link



# def save_pdf_to_model(student_id, course_id, end_date, request):
#     student = Student.objects.get(id=student_id).user
#     student_name = f"{student.first_name} {student.last_name}"
#     course = FreeCourse.objects.get(id=course_id).name
#     file_name = f'{student}_{course}_certificate.pdf'
    
#     template = get_template('certificate/certificate_fast_track.html')
#     context = {"student_name": student_name, "course_name": course, "end_date": end_date}
#     html_content = template.render(context)

#     # Generate PDF using WeasyPrint
#     pdf_file = BytesIO()
#     HTML(string=html_content).write_pdf(pdf_file)

#     pdf_file.seek(0)
#     pdf_content = pdf_file.read()
#     pdf_file.close()

#     joined_student = FreeCourseJoinee.objects.filter(course_id=course_id, student_id=student_id, is_certificate=True).first()
#     if joined_student:
#         joined_student.certificate.save(file_name, ContentFile(pdf_content))
#         joined_student.save()

#     if joined_student and joined_student.certificate:
#         download_link = request.build_absolute_uri(joined_student.certificate.url)
#     else:
#         download_link = None
    
#     return download_link

# def send_email_for_certificate(download_link, email, message, subject):
#     try:
#         check_email = User.objects.filter(email=str(email).strip())
#         if not check_email.exists():
#             return False, "no email"
#         get_user = check_email.first()
        
#         student_name = f"{get_user.first_name} {get_user.last_name}"

#         html_message = f"""<div style="background-color:#f4f4f4;">
#                 <div style="margin:0px auto;border-radius:0px;max-width:600px;" >
#                 <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;border-radius:0px;">
#                     <tbody>
#                     <tr>
#                         <td style="font-size:0px;padding:5px 10px 5px 10px;text-align:center;">
#                         <div class="mj-column-per-100 mj-outlook-group-fix" style="font-size:0px;display:inline-block;vertical-align:top;width:100%;">
#                             <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
#                             <tbody>
#                                 <tr>
#                                 <td align="center" style="font-size:0px;padding:0 0px 20px 0px;word-break:break-word;">
#                                     <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
#                                     <tbody>
#                                         <tr>
#                                         <td style="width:560px;">
#                                             <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;width: 100%;">
#                                             <tbody>
#                                                 <tr>
#                                                 <td style="background-color: #fff;border-radius: 20px;padding: 15px 20px;">
#                                                     <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;width: 100%;">
#                                                     <tbody>
#                                                         <tr>
#                                                         <td height="20"></td>
#                                                         </tr>
#                                                         <tr>
#                                                         <td height="30"></td>
#                                                         </tr>
#                                                         <tr>
#                                                         <td>
#                                                             <table border="0" cellpadding="0" cellspacing="0" role="presentation"  bgcolor="#F6F6F6" style="border-collapse:collapse;border-spacing:0px;width: 100%; border-radius: 6px;">
#                                                             <tbody>
#                                                                 <tr>
#                                                                 <td height="20"></td>
#                                                                 </tr>
#                                                                 <tr>
#                                                                 <td style="padding:20px 25px 0 25px;">
#                                                                     <p style=" font-size: 20px; font-weight: 500; line-height: 22px; color: #333333; margin: 0; padding: 0;">Dear {student_name},</p>
#                                                                 </td>
#                                                                 </tr>
#                                                                 <tr>
#                                                                 <td style="padding:0 25px 20px 25px;">
#                                                                     <p style="font-size: 14px;font-weight: 500;color:#333333">{message}</p>
#                                                                     <br>
#                                                                     <p style="font-size: 14px;font-weight: 500;color:#333333">Click here to download your certificate : - 
#                                                                     <a href="{download_link}" target="_blank" style="color: #1a73e8;">Download Certificate</a>
#                                                                     </p>
#                                                                 </td>
#                                                                 </tr>
#                                                             </tbody>
#                                                             </table>
#                                                         </td>
#                                                         </tr>
#                                                         <tr>
#                                                         <td height="20"></td>
#                                                         </tr>
                                                        
#                                                         <tr>
#                                                         <td height="10"></td>
#                                                         </tr>
#                                                     </tbody>
#                                                     </table>
#                                                 </td>
#                                                 </tr>
#                                             </tbody>
#                                             </table>
#                                         </td>
#                                         </tr>
#                                     </tbody>
#                                     </table>
#                                 </td>
#                                 </tr>
#                             </tbody>
#                             </table>
#                         </div>
#                         </td>
#                     </tr>
#                     </tbody>
#                 </table>
#                 </div>
#             </div>"""

#         send_mail(
#             subject,
#             message,
#             'support@maangcareers.com', # Replace with your email address
#             [get_user.email],
#             fail_silently=False,
#             html_message=html_message,
#         )
#         return True
#     except Exception as e:
#         return False


from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def send_email_for_certificate(download_link, email, course_name):
    print(download_link)
    try:        
        check_email = User.objects.filter(email=str(email).strip())
        if not check_email.exists():
            return False, "no email"
        get_user = check_email.first()
        
        student_name = f"{get_user.first_name} {get_user.last_name}"
        email_config = settings.SUPPORT_EMAIL_CONFIG
    

        connection = get_connection(
            backend=settings.EMAIL_BACKEND,
            host=email_config['EMAIL_HOST'],
            port=email_config['EMAIL_PORT'],
            username=email_config['EMAIL_HOST_USER'],
            password=email_config['EMAIL_HOST_PASSWORD'],
            use_tls=email_config['EMAIL_USE_TLS']
        )
        to = [email]
        subject = f'Course Completion Certificate'
        context = {
        'student_name': student_name,
        'download_link':download_link,
        'course_name': course_name,
        }
        
        template_path = 'email/certificate.html'
        message = render_to_string(template_path, context)

        plain_message = strip_tags(message)        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=email_config['EMAIL_HOST_USER'],
            to=to,
            connection=connection,
        )
        email.attach_alternative(message, "text/html")
        email.send()
        return True
    except Exception as e:        
        return False
