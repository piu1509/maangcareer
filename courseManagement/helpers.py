from courseManagement.models import *
from userManagement.models import Student
from django.utils import timezone

from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.html import strip_tags


def send_email_for_emi_reminder(email, course_name, due_date, due_amount, emi_number):
    
    try:        
        check_email = User.objects.filter(email=str(email).strip())
        if not check_email.exists():
            return False, "no email"
        get_user = check_email.first()
        
        student_name = f"{get_user.first_name} {get_user.last_name}"
        email_config = settings.PAYMENT_EMAIL_CONFIG
    

        connection = get_connection(
            backend=settings.EMAIL_BACKEND,
            host=email_config['EMAIL_HOST'],
            port=email_config['EMAIL_PORT'],
            username=email_config['EMAIL_HOST_USER'],
            password=email_config['EMAIL_HOST_PASSWORD'],
            use_tls=email_config['EMAIL_USE_TLS']
        )
        to = [email]
        payment_url = ''
        subject = f'EMI Reminder'
        context = {
        'student_name': student_name,
        'payment_url':payment_url,
        'course_name': course_name,
        'due_date':due_date,
        'due_amount':due_amount,
        'emi_number':emi_number
        }
        
        template_path = 'email/emi_reminder.html'
        message = render_to_string(template_path, context)
        plain_message = strip_tags(message)

        # email = EmailMessage(subject, message, from_email, to)
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

def send_emi_reminder_email(student_id, batch_id, duration):
    student = Student.objects.get(id=student_id)
    batch = Batch.objects.get(id=batch_id)
    check_batch_joined = BatchJoined.objects.filter(student=student, batch=batch)
    if check_batch_joined.exists():
        batch_joined = check_batch_joined.first()        
        emi_details = batch_joined.choice_emi_type
        if emi_details and emi_details.instament_number > 1:
            emi_payments = StudentEmi.objects.filter(batch=batch, student=student).order_by('emi_number')
            next_instalment_number = len(emi_payments) + 1  # Next installment number

            if emi_payments and next_instalment_number <= emi_details.instament_number:
                last_payment = emi_payments.last()
                last_payment_date = last_payment.created_at.date() 
                
                next_payment_due_date = last_payment_date + timedelta(days=duration)
                reminder_dates = [
                    next_payment_due_date - timedelta(days=7),  # 7 days before due date
                    next_payment_due_date - timedelta(days=2)   # 2 days before due date
                ]
                today_date = timezone.now().date()
                due_amount = InstamentDetails.objects.filter(instalment=next_instalment_number, emi_type=emi_details).first().amount
                check_previous_mail = EmiReminderStatusLog.objects.filter(student=student, batch=batch, status=True, emi_number=next_instalment_number, emi_amount=due_amount)
                if today_date in reminder_dates and not check_previous_mail.filter(reminder_date=today_date):
                    # Send the reminder email
                    course_name = batch.course.name
                    email = student.user.email
                    due_date = next_payment_due_date
                    
                    emi_number = next_instalment_number
                    status = send_email_for_emi_reminder(email, course_name, due_date, due_amount, emi_number) 
                    if status:
                        EmiReminderStatusLog.objects.create(
                            student=student, batch=batch, status=True, emi_number=next_instalment_number, 
                            emi_amount=due_amount, reminder_date=today_date
                        )
                    else:
                        EmiReminderStatusLog.objects.create(
                            student=student, batch=batch, status=False, emi_number=next_instalment_number, 
                            emi_amount=due_amount, reminder_date=today_date
                        )
                    print(f'Reminder email sent to {student.user.username} for EMI installment {next_instalment_number}.')
                else:
                    print(f'It is not time to send the reminder email yet. {today_date} is not in {reminder_dates}.')
            else:
                print(f'All installments have been paid for student {student.user.username} in batch {batch.name}.')
        else:
            print(f'No valid EMI details found for student {student.user.username} in batch {batch.name}.')
    else:
        print(f'No BatchJoined entry found for student {student.user.username} and batch {batch.name}.')


def send_mail_for_all_student():
    check_batch_joined = BatchJoined.objects.filter(full_payment_status= False, choice_emi_type__isnull=False)
    if check_batch_joined.exists():
        for i in check_batch_joined:
            batch = i.batch
            student = i.student
            duration = i.choice_emi_type.emi_duration
            send_emi_reminder_email(student.id, batch.id, duration)
        return True
    else:
        return False   


def send_mail_for_welcome(email):
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
        subject = f'Welcome To MAANGCareers!!'
        template_path = 'email/welcome.html'
        context = {
            "student_name": student_name
        }
        message = render_to_string(template_path, context)
        plain_message = strip_tags(message)
        # email = EmailMessage(subject, message, from_email, to)
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


def send_mail_for_otp(email, otp):
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
        subject = f'OTP VERIFICATION For Login'
        template_path = 'email/otp.html'
        context = {
            "student_name": student_name,
            "otp":list(str(otp))
        }
        message = render_to_string(template_path, context)
        # email = EmailMessage(subject, message, from_email, to)
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


def send_mail_for_reset_password(email, reset_link):
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
        subject = f'Reset Password Link'
        template_path = 'email/reset_password.html'
        context = {
            "student_name": student_name,
            "reset_password_link":reset_link
        }
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


def send_email_for_payment_clear(download_link, email, course_name):
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
        
        template_path = 'email/payment_clear_request.html'
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
