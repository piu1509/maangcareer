from django.contrib.auth import login
from django.contrib.auth.models import User
from userManagement.models import *
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.serializers import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from knox.views import LoginView as KnoxLoginView
from django_otp.oath import TOTP
from django.core.mail import send_mail
from django_otp.plugins.otp_totp.models import TOTPDevice
import hashlib
from rest_framework.response import Response
from django.contrib.auth import authenticate
from knox.models import AuthToken
import time
from knox.auth import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from courseManagement.models import *
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from courseManagement.helpers import send_mail_for_otp, send_mail_for_welcome, send_mail_for_reset_password
from rest_framework.exceptions import APIException
from django.db.models import Q
from adminSalesManagement.serializers import *
from collections import defaultdict
from dateutil import parser
from django.db.models import Max, FloatField, OuterRef, Subquery, Count


# Create your views here.

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


class CustomValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A validation error occurred.'
    default_code = 'invalid'

    def __init__(self, detail, code=None):
        self.detail = detail
        self.code = code


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
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CustomValidationError({"status": "400", "message": "User Does not exist"})
        
        if not user.check_password(password):
            raise CustomValidationError({"status": "400", "message": "Incorrect Credentials"})
        
        if not user.is_active:
            otp = generate_otp_for_mail(user.email, "login")
            send_mail_for_otp(user.email, otp)
            raise CustomValidationError({"status": "400", "message": "User Not Verified"})
        
        otp = generate_otp_for_mail(user.email, "login")
        send_mail_for_otp(user.email, otp)

        sales_person = SalesPerson.objects.filter(user=user).first()
        if sales_person:
            sales_person.otp = otp
            sales_person.otp_validation_time = timezone.now() + timedelta(minutes=5)
            sales_person.save()
        
        return {
            "username": username,
            "otp_sent": True,
            "message": "OTP sent successfully."
        }


class SalesPersonOTPVerificationView(KnoxLoginView):
    permission_classes = (AllowAny,)

    def post(self, request):
        otp = request.data.get('otp')
        username = request.data.get('username')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User does not exist."})
        
        sales_person = SalesPerson.objects.filter(user=user).first()
        if sales_person:
            if sales_person.otp == int(otp) and sales_person.otp_validation_time >= timezone.now():
                # OTP is valid, generate token
                login(request, user)
                return super().post(request)
            else:
                return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid OTP or OTP expired."})
        else:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User is not a Sales Person."})
                 

class SalesPersonLoginView(KnoxLoginView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        
        username = request.data.get('username')
        password = request.data.get('password')        
       
        serializer = CustomAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Return response indicating OTP has been sent
        return Response({
            "status": status.HTTP_200_OK,
            "message": "OTP sent to your email.",
            "otp_sent": validated_data.get("otp_sent")
        })


class SalesPersonResendOTPView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User does not exist."})

        if not user.is_active:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "User is not verified."})
       
        otp = generate_otp_for_mail(user.email, "login")
        send_mail_for_otp(user.email, otp)

        sales_person = SalesPerson.objects.filter(user=user).first()
        if sales_person:
            sales_person.otp = otp
            sales_person.otp_validation_time = timezone.now() + timedelta(minutes=5)
            sales_person.save()

            return Response({
                "status": status.HTTP_200_OK,
                "message": "OTP has been resent successfully."
            })
        else:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "User is not a Sales Person."
            })


class UserProfileView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        res = {}
        user = request.user
        user_data = SalesPerson.objects.filter(user=user)
        if user_data.exists():
            get_user_details = user_data.first()
            # Access the serialized data
            user_details = SalesPersonSerializer(get_user_details).data
            leave_record = LeaveRecord.objects.filter(user=user)
            # Access the serialized data
            leave_record_data = LeaveRecordSerializer(leave_record, many=True).data
            expense_type = ExpenseType.objects.filter(type="Salary").first()
            salary_list = Expense.objects.filter(to_user=user,to_user_type="sales", expense_type=expense_type,status=True)
            expenses = ExpenseSerializer(salary_list, many=True).data
            
            res["user"] = user_details
            res["leave_data"] = leave_record_data
            res["payment_data"] = expenses
            res["status"] = status.HTTP_200_OK
            res["message"] = None
        else:
            res["user"] = {}
            res["leave_data"] = []
            res["payment_data"] = []
            res["status"] = status.HTTP_401_UNAUTHORIZED
            res["message"] = "UNAUTHORIZED USER"

        return Response(res)


class LeaveRecordCreateView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = LeaveRecordCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, user_type="sales") 
            return Response({"message": "Leave record created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ChangePasswordView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_id = request.user.id
        obj_user = User.objects.get(id=user_id)
        old_password = request.data.get("old_password")
        password1 = request.data.get("password")
        password2 = request.data.get("confirm_password")
        if len(old_password) != 0 and len(password1) != 0 and len(password2) != 0 and password1 != None and password2 != None and password1 == password2:
            if obj_user.check_password(old_password) :
                password = make_password(password1)
                obj_user.password = password
                obj_user.save()
                check_sales_person = SalesPerson.objects.filter(user=obj_user)
                if check_sales_person:
                    sales_person = check_sales_person.first()
                    sales_person.password_raw = password1
                    sales_person.save()
                return Response({"message":"Password updated successfully.", "status":status.HTTP_200_OK})
            else:
                return Response({"message":"Old password does not match.", "status":status.HTTP_400_BAD_REQUEST})
        else:
            return Response({"message":"Password and Confirm password does not match.", "status":status.HTTP_400_BAD_REQUEST})

