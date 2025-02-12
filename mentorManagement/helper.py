import boto3
from botocore.exceptions import ClientError
from django.core.mail import send_mail
from django.contrib.auth.models import User

def sen_message(email, message):
    return f"Send the email in {email} Id. and message is {message}"

def send_email_std(download_link, email, message, subject):
    try:
        check_email = User.objects.filter(email=str(email).strip())
        if not check_email.exists():
            return False, "no email"
        get_user = check_email.first()
        
        student_name = f"{get_user.first_name} {get_user.last_name}"

        html_message = f"""<div style="background-color:#f4f4f4;">
                <div style="margin:0px auto;border-radius:0px;max-width:600px;" >
                <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;border-radius:0px;">
                    <tbody>
                    <tr>
                        <td style="font-size:0px;padding:5px 10px 5px 10px;text-align:center;">
                        <div class="mj-column-per-100 mj-outlook-group-fix" style="font-size:0px;display:inline-block;vertical-align:top;width:100%;">
                            <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                            <tbody>
                                <tr>
                                <td align="center" style="font-size:0px;padding:0 0px 20px 0px;word-break:break-word;">
                                    <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                                    <tbody>
                                        <tr>
                                        <td style="width:560px;">
                                            <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;width: 100%;">
                                            <tbody>
                                                <tr>
                                                <td style="background-color: #fff;border-radius: 20px;padding: 15px 20px;">
                                                    <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;width: 100%;">
                                                    <tbody>
                                                        <tr>
                                                        <td height="20"></td>
                                                        </tr>
                                                        <tr>
                                                        <td height="30"></td>
                                                        </tr>
                                                        <tr>
                                                        <td>
                                                            <table border="0" cellpadding="0" cellspacing="0" role="presentation"  bgcolor="#F6F6F6" style="border-collapse:collapse;border-spacing:0px;width: 100%; border-radius: 6px;">
                                                            <tbody>
                                                                <tr>
                                                                <td height="20"></td>
                                                                </tr>
                                                                <tr>
                                                                <td style="padding:20px 25px 0 25px;">
                                                                    <p style=" font-size: 20px; font-weight: 500; line-height: 22px; color: #333333; margin: 0; padding: 0;">Dear {student_name},</p>
                                                                </td>
                                                                </tr>
                                                                <tr>
                                                                <td style="padding:0 25px 20px 25px;">
                                                                    <p style="font-size: 14px;font-weight: 500;color:#333333">{message}</p>
                                                                    <br>
                                                                    <p style="font-size: 14px;font-weight: 500;color:#333333">Click here : - {download_link}</p>
                                                                </td>
                                                                </tr>
                                                            </tbody>
                                                            </table>
                                                        </td>
                                                        </tr>
                                                        <tr>
                                                        <td height="20"></td>
                                                        </tr>
                                                        
                                                        <tr>
                                                        <td height="10"></td>
                                                        </tr>
                                                    </tbody>
                                                    </table>
                                                </td>
                                                </tr>
                                            </tbody>
                                            </table>
                                        </td>
                                        </tr>
                                    </tbody>
                                    </table>
                                </td>
                                </tr>
                            </tbody>
                            </table>
                        </div>
                        </td>
                    </tr>
                    </tbody>
                </table>
                </div>
            </div>"""

        send_mail(
            subject,
            message,
            'support@maangcareers.com', # Replace with your email address
            [get_user.email],
            fail_silently=False,
            html_message=html_message,
        )
        return True
    except Exception as e:
        return False


def main_send_email(subject, body, to_address, from_address):
    aws_access_key = 'your-access-key'
    aws_secret_key = 'your-secret-key'
    region = 'us-east-1'
    ses = boto3.client('ses', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region)
    sender = from_address
    recipient = to_address
    email_subject = subject
    email_body = body
    message = {
        'Subject': {
            'Data': email_subject
        },
        'Body': {
            'Text': {
                'Data': email_body
            }
        }
    }

    try:
        # Send the email
        response = ses.send_email(
            Source=sender,
            Destination={
                'ToAddresses': [recipient],
            },
            Message=message
        )
        print(f"Email sent! Message ID: {response['MessageId']}")

    except ClientError as e:
        print(f"Error sending email: {e.response['Error']['Message']}")

# Example usage
main_send_email(
    subject='Test Email',
    body='This is a test email sent from Amazon SES using Python.',
    to_address='recipient@example.com',
    from_address='sender@example.com'
)