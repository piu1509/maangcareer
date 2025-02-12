from django.contrib.auth import login
from django.contrib.auth.models import User
from userManagement.models import Student

from rest_framework.serializers import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from rest_framework.generics import CreateAPIView
from knox.views import LoginView as KnoxLoginView
from django_otp.oath import TOTP
from django.core.mail import send_mail
from django_otp.plugins.otp_totp.models import TOTPDevice
import hashlib
from rest_framework.response import Response
from django.contrib.auth import authenticate
from knox.models import AuthToken
import time
from rest_framework.views import APIView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from courseManagement.helpers import send_mail_for_otp, send_mail_for_welcome, send_mail_for_reset_password
from django.utils import timezone
from datetime import timedelta


class KonxLoginUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            # 'id',
            'first_name',
            'last_name',
            'email',
            'student'
        )
        depth = 1


class CustomAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"err_code": "User Does not exist"})

        # Check if user is inactive
        if not user.is_active:
            otp = generate_otp_for_mail(user.email, "login")           
            user.student.otp = otp
            user.student.otp_expiry = timezone.now() + timedelta(seconds=120)  # Setting OTP expiry to 2 minutes
            user.student.save()

            send_mail_for_otp(user.email, otp)
            raise serializers.ValidationError({"err_code": "Your account is not verified. Please check your email for OTP verification."})

        # Authenticate user if active
        if username and password:
            authenticate_user = authenticate(
                request=self.context.get('request'),
                username=username, 
                password=password
            )
            if not authenticate_user:
                raise serializers.ValidationError({"err_code": "Incorrect Credentials"})
        else:
            raise serializers.ValidationError({"err_code": "Username and Password are required."})
        
        return authenticate_user


class LoginView(KnoxLoginView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        try:
            # Set new password if provided
            new_password = request.data.get("password")
            user = User.objects.filter(username=request.data.get("username")).first()
            if user:
                user.set_password(new_password)

            # Validate credentials and active status using CustomAuthTokenSerializer
            serializer = CustomAuthTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Log the user in if validation passed
            user = serializer.validated_data
            
            login(request, user)
            
            return super(LoginView, self).post(request, format=None)
        except ValidationError as e:
            # Handle validation errors like 'user not found' or 'not verified'
            raise e


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            "username": {"validators": [], },
        }
  

class StudentSerialzer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = '__all__'

    def validate(self, attrs):
            user=User.objects.filter(username=attrs.get("user")['username'])
            if user:
                if user[0].is_active:
                    raise ValidationError({"err_code": "A user with that username already exists."})
                raise ValidationError({"err_code": "user is not verified."})
            return attrs

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['is_active'] = False
        user = User.objects.create_user(**user_data)
        student = Student.objects.create(user=user,**validated_data)
        return student


def get_active_user_from_query(**kwargs) -> User:
    """get active and inactive user"""
    try:
        return User.objects.get(**kwargs)
    except User.DoesNotExist:
        raise ValidationError({"err_code": "User Does Not Exists"})


class EmailVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(required=False, max_length=6)

    def validate(self, data):
        user = get_active_user_from_query(email__iexact=data.get("email"))
        return user


class GeneratingOTP:
    def __init__(self, email, extra_key, user=None):
        if not user:
            user = User.objects.get(email__iexact=email)
        self.user = user
        hex_email = self.generate_hex(
            self.user.email or self.user.phone_number.as_e164, 20
        )
        hex_extra_key = self.generate_hex(extra_key, 20)
        self.key = f"{hex_email}{hex_extra_key}"
        self.number_of_digits = 6
        # validity period of a token. Default is 30 second.
        self.token_validity_period = 3 * 60

    @staticmethod
    def generate_hex(value, length):
        sha256_hash = hashlib.sha256(value.encode()).hexdigest()
        hex_string = sha256_hash[:length]
        return hex_string

    def totp_device(self):
        totp_device, created = TOTPDevice.objects.update_or_create(
            key=self.key,
            user=self.user,
            defaults={
                "step": self.token_validity_period,
                "digits": self.number_of_digits,
                "tolerance": 0,
            },
        )
        return totp_device

    def totp_obj(self):
        totp_device = self.totp_device()
        # create a TOTP object
        totp = TOTP(
            key=totp_device.bin_key,
            step=totp_device.step,
            t0=totp_device.t0,
            digits=totp_device.digits,
            drift=totp_device.drift,
        )
        return totp

    def generate_otp(self):
        # get the TOTP object and use that to create token
        totp = self.totp_obj()
        token = totp.token()
        return str(token).zfill(self.number_of_digits)

    def verify_otp(self, token):
        # verify otp using totp device
        totp_device = self.totp_device()
        is_verified = totp_device.verify_token(token)
        if is_verified:
            totp_device.delete()
        return is_verified


def generate_otp_for_mail(
        email: str,
        extra_key: str,
) -> bool:
    """Generate OTP for Phone Number"""
    generate_otp_service = GeneratingOTP(email, extra_key)

    return generate_otp_service.generate_otp()


def verify_otp_for_mail(email: str, extra_key: str, otp: int):
    """Verify the OTP"""
    verified_otp = GeneratingOTP(email, extra_key)
    if not verified_otp.verify_otp(otp):
        raise Exception("INVALID_OTP")
    user_otp = verified_otp.generate_otp()
    if int(user_otp) != int(otp):
        raise Exception("OTP EXPIRED")


class SignUpView(CreateAPIView):
    serializer_class = StudentSerialzer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            student = serializer.save()

            # Generate OTP and set expiration
            otp = generate_otp_for_mail(student.user.email, "registration")
            student.otp = otp
            student.otp_expiry = timezone.now() + timedelta(seconds=120)  # OTP valid for 5 minutes
            student.save()

            # Send OTP to email
            send_mail_for_otp(student.user.email, otp)
            return Response({'msg': "OTP has been sent to your email."}, status=status.HTTP_201_CREATED)

        raise ValidationError(serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        try:
            serializer = EmailVerifySerializer(context={"request": request}, data=request.data)
            serializer.is_valid(raise_exception=True)

            otp = request.data.get("otp")
            if not otp:
                raise ValidationError({"err_code": "OTP is required."})

            # Fetch the user from the serializer data
            user = serializer.validated_data

            # Check OTP validity from the student instance
            student = user.student
            if not student.is_otp_valid():
                raise ValidationError({"err_code": "OTP is invalid or has expired."})

            if student.otp != otp:
                raise ValidationError({"err_code": "The OTP you entered is incorrect."})

            extra_key = request.data.get("extra_key", "").lower()

            if extra_key == "registration":
                user.is_active = True
                user.save()
                send_mail_for_welcome(user.email)
                user.last_login = timezone.now()
                user.save()
                return Response({"msg": "OTP Verified Successfully. Your account has been activated."})

            elif extra_key == "login":
                user.is_active = True
                user.save()
                _, token = AuthToken.objects.create(user)
                if user.last_login is None:
                    send_mail_for_welcome(user.email)
                return Response({
                    "token": token,
                    "user": {
                        "username": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "student": {
                            "id": user.student.id,
                            "phone_num": user.student.phone_num,
                            "joined_date": user.student.joined_date,
                            "profile_img": "" if not user.student.profile_img else user.student.profile_img.url,
                            "terms_condition": user.student.terms_condition,
                            "user": user.id
                        }
                    }
                })

        except ValidationError as e:
            raise e

        except Exception as error:
            return Response({"err_code": f"str(error)"}, status=400)


from rest_framework.generics import GenericAPIView


class ResendOTpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    extra_key = serializers.CharField(max_length=256)

    def validate(self, data):
        user = get_active_user_from_query(email__iexact=data.get("email"))
        return user


class ResendOtpAPIView(GenericAPIView):
    permission_classes = [AllowAny]

    serializer_class = ResendOTpSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(context=request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data
            extra_key = request.data["extra_key"].lower()
            auto_fill_key = request.data.get("auto_fill_key", None)
            if extra_key:
                otp = generate_otp_for_mail(user.email, extra_key)
               
                user.student.otp = otp
                user.student.otp_expiry = timezone.now() + timedelta(seconds=60)
                user.student.save()
                # subject = 'OTP VERIFICATION'
                # message = f'Your OTP is {otp}'
                # from_email = 'kalalharsh708@gmail.com'
                # recipient_list = [user.email]
                # send_mail(subject, message, from_email, recipient_list)
                send_mail_for_otp(user.email, otp)
            else:
                return Response(
                    {"err_code": "Invalid Request"}
                )
            response = {
                'msg': "OTP has been sent to your mail"
            }
            return Response(response, status=status.HTTP_200_OK)
        except KeyError as ke:
            return Response({"err_code": f"{ke} is required"})
        except ValidationError as e:
            raise e
        except Exception as e:
            return Response({"err_code": str(e)})



### New added for reset password

class PasswordResetRequestView(APIView):
    def post(self, request):
        data = {'status':'', 'message':''}
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            data['status'] = status.HTTP_400_BAD_REQUEST
            data['message'] = "User with this email does not exist."
            return Response(data)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        frontend_url = f"https://dev.maangcareers.in/createpassword?uid={uid}&token={token}"

        send_mail_for_reset_password(user.email, frontend_url)
        data['status'] = status.HTTP_200_OK
        data['message'] = "Password reset link has been sent to your email."
        return Response(data)


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data


class PasswordResetConfirmView(APIView):
    def post(self, request):
        data= {'status':'', 'message':''}
        uidb64 = request.data.get('uid')
        token = request.data.get('token')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            data['status'] = status.HTTP_400_BAD_REQUEST
            data['message'] = "Invalid link."
            return Response(data)

        if not default_token_generator.check_token(user, token):
            data['status'] = status.HTTP_400_BAD_REQUEST
            data['message'] = "Invalid or expired token."
            return Response(data)

        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            data['status'] = status.HTTP_200_OK
            data['message'] = "Password has been reset successfully."
            return Response(data)
        data['status'] = status.HTTP_400_BAD_REQUEST
        data['message'] = f"{serializer.errors}"
        return Response(data)
