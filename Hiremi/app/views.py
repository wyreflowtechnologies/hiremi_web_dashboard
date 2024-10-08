import random, json, traceback, requests
from uuid import uuid4
from rest_framework import generics, status, viewsets,mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from paytmchecksum import PaytmChecksum
from django.core.mail import send_mail
from threading import Thread
from .email import *
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError,AuthenticationFailed
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
from django.db import DatabaseError
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth import  login,authenticate,logout
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = Register.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Start a database transaction
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                
                user = serializer.instance
                
                subject = 'Welcome to HireMi'
                message = (
                    f"Hi {user.full_name},\n\n"
                    f"Thank you for registering at HireMi! We are excited to have you join our community.\n\n"
                    f"As a member, you now have access to all our features and services. Feel free to explore and take advantage of everything we offer.\n\n"
                    f"If you have any questions or need assistance, don't hesitate to contact our support team.\n\n"
                    f"Best regards,\n"
                    f"The HireMi Team"
                )
                recipient_list = [user.email]
                
                # Send the email asynchronously
                self.send_custom_email_async(subject, message, recipient_list)
                
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def send_custom_email_async(self, subject, message, recipient_list):
        # Use a thread to send the email asynchronously
        email_thread = Thread(target=send_custom_email, args=(subject, message, recipient_list))
        email_thread.start()
    


# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Check if the user exists with the given email
            try:
                user = Register.objects.get(email=email)
            except ObjectDoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

            # Authenticate the user
            user = authenticate(request, email=email, password=password)
            if user is not None:
                return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)

        except ValidationError as ve:
            return Response({"error": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as oe:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except AuthenticationFailed as af:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #

class ScoreCardViewSet(viewsets.ModelViewSet):
    queryset = ScoreCard.objects.all()
    serializer_class = ScoreCardSerializer

    def get_queryset(self):
        register_id = self.request.query_params.get('register')
        if register_id:
            return ScoreCard.objects.filter(register__id=register_id)
        return ScoreCard.objects.all()

    def create(self, request, *args, **kwargs):
        register_id = request.data.get('register')
        if not register_id:
            return Response({"error": "register field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            register = Register.objects.get(id=register_id)
        except Register.DoesNotExist:
            return Response({"error": "Register not found."}, status=status.HTTP_404_NOT_FOUND)

        if ScoreCard.objects.filter(register=register).exists():
            return Response({"error": "A scorecard already exists for this register."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"error": "ScoreCard not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


class TransactionDetails(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = PaymentTransaction.objects.all()
    serializer_class = TransactionDetailsSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception:
            return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


class FresherJobViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = FresherJob.objects.all()
    serializer_class = FresherJobSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception:
            return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #

class ExperienceJobViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = ExperienceJob.objects.all()
    serializer_class = ExperienceJobSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception:
            return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #



class InternshipViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Internship.objects.all()
    serializer_class = InternshipSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "Internship deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
    

class VerificationDetailsViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = VerificationDetails.objects.all()
    serializer_class = VerificationDetailsSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred in list method: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            register_id = request.data.get('register')
            print(register_id)
            if VerificationDetails.objects.filter(register_id=register_id).exists():
                return Response({"error": "A verification already exists for this user."}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


class ForgotPasswordOTPView(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                user = Register.objects.filter(email=email).first()

                if user:
                    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                    user.otp = otp
                    user.save()
                    send_mail("Password Reset OTP", f"Your OTP for password reset is: {otp}", settings.EMAIL_HOST_USER, [email], fail_silently=False)
                    request.session['email'] = email
                    return Response({"message": "OTP has been sent to your email.", "email": email}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Email does not exist in the system."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback.print_exc()
            return Response({"message": "Failed to send OTP email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


class OTPValidationView(APIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = OTPValidationSerializer
    def post(self, request, *args, **kwargs):
        try:
            serializer = OTPValidationSerializer(data=request.data)
            print("hilo")
            if 'email' in request.session:
                if serializer.is_valid():
                    email = request.session['email']
                    user = Register.objects.filter(email=email).first()
                    otp = serializer.validated_data['otp']

                    if user and user.otp == otp:
                        return Response({"message": "OTP validated. Proceed with password reset."}, status=status.HTTP_200_OK)

                    return Response({"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Email not found in session."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
class TrainingProgramViewSet(viewsets.ModelViewSet):
    queryset = TrainingProgram.objects.all()
    serializer_class = TrainingProgramSerializer
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
class TrainingProgramApplicationViewSet(viewsets.ModelViewSet):
    queryset = TrainingProgramApplication.objects.all()
    serializer_class = TrainingProgramApplicationSerializer

    # Override the create method to check if the user already applied
    def create(self, request, *args, **kwargs):
        register = request.data.get('register')
        training_program = request.data.get('TrainingProgram')
        
        # Check if the application already exists
        if TrainingProgramApplication.objects.filter(register=register, TrainingProgram=training_program).exists():
            return Response({"error": "You have already applied for this training program."}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)



# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
class PasswordReset(APIView):
    serializer_class = ResetAccountPasswordSerializer
    def post(self, request):
        try:
            serializer = ResetAccountPasswordSerializer(data=request.data)
            if serializer.is_valid():
                email = request.session.get('email')
                if email:
                    user = Register.objects.filter(email=email).first()
                    if user:
                        pass1 = serializer.validated_data['pass1']
                        pass2 = serializer.validated_data['pass2']

                        if pass1 == pass2:
                            user.password = make_password(pass1)
                            user.save()
                            
                            # Send email upon successful password reset
                            send_password_reset_email(email)

                            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
                        return Response({"message": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
                    return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
                return Response({"message": "Email not found in session."}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


# class JobApplicationViewSet(viewsets.ModelViewSet):
#     queryset = JobApplication.objects.all()
#     serializer_class = JobApplicationSerializer

#     def perform_create(self, serializer):
#         try:
#             with transaction.atomic():
#                 serializer.save()
#         except Exception as e:
#             return Response({"error": "An unexpected error occurred while saving the job application. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def create(self, request, *args, **kwargs):
#         try:
#             register_id = request.data.get('register')
#             fresherjob_id = request.data.get('fresherjob')
            
#             if not register_id or not fresherjob_id:
#                 return Response({"error": "Both register and fresherjob fields are required."}, status=status.HTTP_400_BAD_REQUEST)
            
#             # Check if the register and fresher job exist
#             register_exists = Register.objects.filter(id=register_id).exists()
#             fresherjob_exists = FresherJob.objects.filter(id=fresherjob_id).exists()
            
#             if not register_exists:
#                 return Response({"error": "Register not found."}, status=status.HTTP_404_NOT_FOUND)
#             if not fresherjob_exists:
#                 return Response({"error": "Fresher job not found."}, status=status.HTTP_404_NOT_FOUND)
            
#             # Proceed with creating the application
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             headers = self.get_success_headers(serializer.data)
#             return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
#         except Exception as e:
#             return Response({"error": f"An unexpected error occurred: {str(e)}. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
        except Exception as e:
            return Response({"error": "An unexpected error occurred while saving the job application. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            register_id = request.data.get('register')
            fresherjob_id = request.data.get('fresherjob')
            
            if not register_id or not fresherjob_id:
                return Response({"error": "Both register and fresherjob fields are required."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if the register and fresher job exist
            register_exists = Register.objects.filter(id=register_id).exists()
            fresherjob_exists = FresherJob.objects.filter(id=fresherjob_id).exists()
            
            if not register_exists:
                return Response({"error": "Register not found."}, status=status.HTTP_404_NOT_FOUND)
            if not fresherjob_exists:
                return Response({"error": "Fresher job not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if the application already exists
            application_exists = JobApplication.objects.filter(register_id=register_id, fresherjob_id=fresherjob_id).exists()
            if application_exists:
                return Response({"error": "You have already applied for this fresher job."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Proceed with creating the application
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


# class ExperienceJobApplicationViewSet(viewsets.ModelViewSet):
#     queryset = ExperienceJobApplication.objects.all()
#     serializer_class = ExperienceJobApplicationSerializer

#     def perform_create(self, serializer):
#         try:
#             with transaction.atomic():
#                 serializer.save()
#         except Exception as e:
#             return Response({"error": "An unexpected error occurred while saving the job application. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def create(self, request, *args, **kwargs):
#         try:
#             register_id = request.data.get('register')
#             experiencejob_id = request.data.get('experiencejob')
            
#             if not register_id or not experiencejob_id:
#                 return Response({"error": "Both register and experience fields are required."}, status=status.HTTP_400_BAD_REQUEST)
            
#             # Check if the register and fresher job exist
#             register_exists = Register.objects.filter(id=register_id).exists()
#             experience_job_exists = ExperienceJob.objects.filter(id=experiencejob_id).exists()
            
#             if not register_exists:
#                 return Response({"error": "Register not found."}, status=status.HTTP_404_NOT_FOUND)
#             if not experience_job_exists:
#                 return Response({"error": "Experience job not found."}, status=status.HTTP_404_NOT_FOUND)
            
#             # Proceed with creating the application
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             headers = self.get_success_headers(serializer.data)
#             return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
#         except Exception as e:
#             return Response({"error": f"An unexpected error occurred: {str(e)}. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExperienceJobApplicationViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = ExperienceJobApplication.objects.all()
    serializer_class = ExperienceJobApplicationSerializer

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
        except Exception as e:
            return Response({"error": "An unexpected error occurred while saving the job application. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            register_id = request.data.get('register')
            experiencejob_id = request.data.get('experiencejob')
            
            if not register_id or not experiencejob_id:
                return Response({"error": "Both register and experience fields are required."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if the register and experience job exist
            register_exists = Register.objects.filter(id=register_id).exists()
            experience_job_exists = ExperienceJob.objects.filter(id=experiencejob_id).exists()
            
            if not register_exists:
                return Response({"error": "Register not found."}, status=status.HTTP_404_NOT_FOUND)
            if not experience_job_exists:
                return Response({"error": "Experience job not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if the application already exists
            application_exists = ExperienceJobApplication.objects.filter(register_id=register_id, experiencejob_id=experiencejob_id).exists()
            if application_exists:
                return Response({"error": "You have already applied for this experience job."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Proceed with creating the application
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


# class InternshipApplicationViewSet(viewsets.ModelViewSet):
#     queryset = InternshipApplication.objects.all()
#     serializer_class = InternshipApplicationSerializer

#     def perform_create(self, serializer):
#         try:
#             with transaction.atomic():
#                 serializer.save()
#         except Exception as e:
#             return Response({"error": "An unexpected error occurred while saving the internship application. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def create(self, request, *args, **kwargs):
#         try:
#             register_id = request.data.get('register')
#             internship_id = request.data.get('internship')
            
#             if not register_id or not internship_id:
#                 return Response({"error": "Both register and internship fields are required."}, status=status.HTTP_400_BAD_REQUEST)
            
#             # Check if the register and internship exist
#             register_exists = Register.objects.filter(id=register_id).exists()
#             internship_exists = Internship.objects.filter(id=internship_id).exists()
            
#             if not register_exists:
#                 return Response({"error": "Register not found."}, status=status.HTTP_404_NOT_FOUND)
#             if not internship_exists:
#                 return Response({"error": "Internship not found."}, status=status.HTTP_404_NOT_FOUND)
            
#             # Proceed with creating the application
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             headers = self.get_success_headers(serializer.data)
#             return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
#         except Exception as e:
#             return Response({"error": f"An unexpected error occurred: {str(e)}. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class InternshipApplicationViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = InternshipApplication.objects.all()
    serializer_class = InternshipApplicationSerializer

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
        except Exception as e:
            return Response({"error": "An unexpected error occurred while saving the internship application. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            register_id = request.data.get('register')
            internship_id = request.data.get('internship')
            
            if not register_id or not internship_id:
                return Response({"error": "Both register and internship fields are required."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if the register and internship exist
            register_exists = Register.objects.filter(id=register_id).exists()
            internship_exists = Internship.objects.filter(id=internship_id).exists()
            
            if not register_exists:
                return Response({"error": "Register not found."}, status=status.HTTP_404_NOT_FOUND)
            if not internship_exists:
                return Response({"error": "Internship not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if the application already exists
            application_exists = InternshipApplication.objects.filter(register_id=register_id, internship_id=internship_id).exists()
            if application_exists:
                return Response({"error": "You have already applied for this internship."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Proceed with creating the application
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


class MentorshipViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Mentorship.objects.all()
    serializer_class = MentorshipSerializer
  
    def create(self, request, *args, **kwargs):
        register_id = request.data.get('register')
        if not register_id:
            return Response({"error": "register field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            register = Register.objects.get(id=register_id)
        except Register.DoesNotExist:
            return Response({"error": "Register not found."}, status=status.HTTP_404_NOT_FOUND)

        if Mentorship.objects.filter(register=register).exists():
            return Response({"error": "User has already applied for mentorship."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


class CorporateViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = CorporateTraining.objects.all()
    serializer_class = CorporateSerializer

    def create(self, request, *args, **kwargs):
        register_id = request.data.get('register')
        if not register_id:
            return Response({"error": "register field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            register = Register.objects.get(id=register_id)
        except Register.DoesNotExist:
            return Response({"error": "Register not found."}, status=status.HTTP_404_NOT_FOUND)

        if CorporateTraining.objects.filter(register=register).exists():
            return Response({"error": "User has already applied for corporate training."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


class DiscountViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "Discount deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Discount.DoesNotExist:
            return Response({"error": "Discount does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


class CorporateDiscountViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = CorporateDiscount.objects.all()
    serializer_class = CorporateDiscountSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "Corporate Discount deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except CorporateDiscount.DoesNotExist:
            return Response({"error": "Corporate Discount does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #

class MentorshipDiscountViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = MentorshipDiscount.objects.all()
    serializer_class = MentorshipDiscountSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "Mentorship Discount deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except MentorshipDiscount.DoesNotExist:
            return Response({"error": "Mentorship Discount does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


class InitiatePaymentRateThrottle(UserRateThrottle):
    rate = '5/minute'  
class InitiatePayment(APIView):
    throttle_classes = [InitiatePaymentRateThrottle]
    @transaction.atomic()
    def post(self, request):
        try:
            serializer = PaymentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            amount = serializer.validated_data['amount']
            email = serializer.validated_data['email']
            order_id = f'order_{uuid4().hex}' # As timestamp may lead to issues

            PAYTM_MID = "216820000000000077910"
            PAYTM_MERCHANT_KEY = "QU%rHGbkHQB%H%OY"
            PAYTM_ENVIRONMENT = 'https://router.paytm.in'
            PAYTM_WEBSITE = 'DEFAULT'

            paytmParams = {
                "body": {
                    "requestType": "PAYMENT",
                    "mid": PAYTM_MID,
                    "websiteName": PAYTM_WEBSITE,
                    "orderId": order_id,
                    "callbackUrl": "http://13.127.246.196:8000/callback/",  # Your callback URL
                    "txnAmount": {
                        "value": str(amount),  # Convert to str for JSON serialization
                        "currency": "INR",
                    },
                    "userInfo": {
                        "custId": 'cust' + str(int(datetime.now().timestamp())),  # Generate unique customer ID
                    },
                }
            }

            checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), PAYTM_MERCHANT_KEY)

            paytmParams["head"] = {
                "signature": checksum
            }
            post_data = json.dumps(paytmParams)
            url = f"{PAYTM_ENVIRONMENT}/aoa-acquiring-biz/v2/order?mid={PAYTM_MID}&orderId={order_id}"
            headers = {"Content-type": "application/json"}

            try:
                response = requests.post(url, data=post_data, headers=headers)
                response.raise_for_status()
                response_data = response.json()

                if response_data["body"]["resultInfo"]["resultStatus"] == 'S':
                    token = response_data["body"]["txnToken"]
                    response_dict = {
                        "txnToken": token,
                        "amount": str(amount),
                        "orderId": order_id,
                    }
                    print("initiated")
                    
                    PaymentTransaction.objects.create(
                        email=email,
                        amount=amount,  # Keep as Decimal when saving to the model
                        txn_token=token,
                        order_id=order_id,
                        is_paid=False
                    )

                    send_payment_initiation_email(email, amount, order_id)
                else:
                    response_dict = {"error": "Payment initiation failed"}

                return Response(response_dict, status=response.status_code)
            
            except requests.exceptions.ConnectionError:
                return Response({"error": "Failed to connect to Paytm server"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except requests.exceptions.Timeout:
                return Response({"error": "Request to Paytm timed out"}, status=status.HTTP_504_GATEWAY_TIMEOUT)
            except requests.exceptions.HTTPError as e:
                return Response({"error": f"HTTP error occurred: {str(e)}"}, status=e.response.status_code)
            except requests.exceptions.RequestException as e:
                return Response({"error": f"An error occurred while making the request: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except json.JSONDecodeError:
                return Response({"error": "Failed to parse Paytm response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
        except ValidationError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as re:
            return Response({"error": "Failed to communicate with payment gateway"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #

class PaytmCallback(APIView):
    def post(self, request):
        serializer = CallbackSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            checksum = data.get('CHECKSUMHASH')
            
            data.pop('CHECKSUMHASH', None)
            verify_signature = PaytmChecksum.verifySignature(data, "QU%rHGbkHQB%H%OY", checksum)
            
            if verify_signature:
                text_success = "Checksum is verified. Transaction details are below."
                # Extract necessary data from the callback
                order_id = data.get('ORDERID')
                status = data.get('STATUS')
                txn_token = data.get('TXNID')
                amount = data.get('TXNAMOUNT')
               
                # Update the database based on the callback status
                try:
                    payment_data = PaymentTransaction.objects.get(order_id=order_id)
                    payment_data.txn_token = txn_token
                    payment_data.amount = amount
                    if status == 'TXN_SUCCESS':
                        payment_data.is_paid = True
                        # Send email upon successful payment confirmation
                        send_payment_confirmation_email(payment_data.email, amount, order_id)
                    else:
                        send_payment_failed_email(payment_data.email, amount, order_id)
                        return Response({'text_error':'Checksum is verified but transaction has failed.'})
                    payment_data.save()
                except PaymentTransaction.DoesNotExist:
                    text_error = f"Payment data for order ID {order_id} not found in the database."
                    return Response({'text_error': text_error})

                return Response({'text_success': text_success, 'verifySignature': verify_signature})
            else:
                text_error = "Checksum is not verified."
                return Response({'text_error': text_error})
        else:
            text_error = "Invalid Request."
            return Response({'text_error':text_error})







# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #


class OrderStatus(APIView):

    def post(self, request):
        serializer = OrderStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        order_id = serializer.validated_data.get('order_id')

        # PAYTM_MID = "216820000000000014719"
        # PAYTM_MERCHANT_KEY = "V2&76JhDi4B6#r8P"
        # PAYTM_ENVIRONMENT = 'https://stage-router.paytm.in'

        PAYTM_MID = "216820000000000077910"
        PAYTM_MERCHANT_KEY = "QU%rHGbkHQB%H%OY"
        PAYTM_ENVIRONMENT = 'https://router.paytm.in'

        paytmParams = {
            "body": {
                "mid": PAYTM_MID,
                "orderId": order_id,
            }
        }
        checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), PAYTM_MERCHANT_KEY)
        paytmParams["head"] = {
            "signature": checksum
        }
        
        post_data = json.dumps(paytmParams)

        url = PAYTM_ENVIRONMENT + "/aoa-order-status/v2/orderstatus/querybyorderid"

        headers = {"Content-type": "application/json"}
        try:
            response = requests.post(url, data=post_data, headers=headers)
            response.raise_for_status()
            response_data = response.json()

            # Extract relevant information from the Paytm response
            result_info = response_data["body"]["resultInfo"]
            txn_status = result_info["resultStatus"]
            txn_msg = result_info["resultMsg"]
            txn_amount = response_data["body"].get("txnAmount")
            txn_id = response_data["body"].get("txnId")

            if txn_status == 'TXN_SUCCESS' or 'Success':
                try:
                    payment_data = PaymentTransaction.objects.get(order_id=order_id)
                    if txn_msg == 'Txn Success':
                        response_dict = {
                            "order_id": order_id,
                            "status": "Success",
                            "amount": payment_data.amount,
                            "txn_id": payment_data.txn_token,
                            "paytm_response": response_data
                        }
                        OrderStatusResponse.objects.update_or_create(
                            order_id=order_id,
                            defaults={
                                "status": "Success",
                                "amount": payment_data.amount,
                                "txn_id": payment_data.txn_token,
                                "result_msg": txn_msg,
                            }
                        )
                    else:
                        response_dict = {
                            "order_id": order_id,
                            "status": "Failed",
                            "amount": payment_data.amount,
                            "txn_id": payment_data.txn_token,
                            "paytm_response": response_data
                        }
                        OrderStatusResponse.objects.update_or_create(
                            order_id=order_id,
                            defaults={
                                "status": "Failed",
                                "amount": payment_data.amount,
                                "txn_id": payment_data.txn_token,
                                "result_msg": txn_msg,
                            }
                        )

                except PaymentTransaction.DoesNotExist:
                    response_dict = {
                        "error": "Payment data not found in the database.",
                        "paytm_response": response_data
                    }
                    OrderStatusResponse.objects.update_or_create(
                        order_id=order_id,
                        defaults={
                            "status": "Failed",
                            "result_msg": "Payment data not found in the database."
                        }
                    )
            else:
                response_dict = {
                    "error": txn_msg,
                    "paytm_response": response_data
                }
                OrderStatusResponse.objects.update_or_create(
                    order_id=order_id,
                    defaults={
                        "status": "Failed",
                        "result_msg": txn_msg
                    }
                )

            return Response(response_dict, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def get(self, request, order_id=None):
        if order_id:
            try:
                order_status_response = OrderStatusResponse.objects.get(order_id=order_id)
                response_serializer = OrderStatusResponseSerializer(order_status_response)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except OrderStatusResponse.DoesNotExist:
                return Response({"error": "Order status not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            order_status_responses = OrderStatusResponse.objects.all()
            response_serializer = OrderStatusResponseSerializer(order_status_responses, many=True)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #




# class QueryCreateAPIView(generics.ListCreateAPIView):
#     queryset = Query.objects.all()
#     serializer_class = QuerySerializer

#     def create(self, request, *args, **kwargs):
#         register_id = request.data.get('register')
#         email = request.data.get('email')

#         # Validate register
#         register = get_object_or_404(Register, id=register_id)

#         # Check if provided email matches the register's email
#         if register.email != email:
#             return Response({"error": "Provided email doesn't match the register's email."}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if the user raised a ticket in the last 15 days
#         last_ticket = Query.objects.filter(register=register).order_by('-created_at').first()
#         if last_ticket:
#             time_difference = timezone.now() - last_ticket.created_at
#             if time_difference < timedelta(days=15):
#                 return Response({"error": "You can only raise a ticket once every 15 days."}, status=status.HTTP_400_BAD_REQUEST)

#         # Proceed with creating the ticket
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
        
#         # Send email upon successful ticket creation
#         send_ticket_creation_email(email)
        
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class QueryViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Query.objects.all()
    serializer_class = QuerySerializer

    def create(self, request, *args, **kwargs):
        register_id = request.data.get('register')
        email = request.data.get('email')

        # Validate register
        register = get_object_or_404(Register, id=register_id)

        # Check if provided email matches the register's email
        if register.email != email:
            return Response({"error": "Provided email doesn't match the register's email."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user raised a ticket in the last 15 days
        last_ticket = Query.objects.filter(register=register).order_by('-created_at').first()
        if last_ticket:
            time_difference = timezone.now() - last_ticket.created_at
            if time_difference < timedelta(days=15):
                return Response({"error": "You can only raise a ticket once every 15 days."}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed with creating the ticket
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Send email upon successful ticket creation
        send_ticket_creation_email(email)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #
# ========================================================================================== #



class BaseViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    def handle_exceptions(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except self.queryset.model.DoesNotExist:
            return Response({'error': f'{self.queryset.model.__name__} not found.'}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError:
            return Response({'error': 'Database error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        return self.handle_exceptions(super().list, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return self.handle_exceptions(super().retrieve, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return self.handle_exceptions(super().create, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return self.handle_exceptions(super().update, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return self.handle_exceptions(super().destroy, request, *args, **kwargs)

class ProfileViewSet(BaseViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class BasicDetailsViewSet(BaseViewSet):
    queryset = BasicDetails.objects.all()
    serializer_class = BasicDetailsSerializer

# class ProfileSummaryViewSet(BaseViewSet):
#     queryset = ProfileSummary.objects.all()
#     serializer_class = ProfileSummarySerializer


class ProfileSummaryViewSet(ModelViewSet):
    queryset = ProfileSummary.objects.all()
    serializer_class = ProfileSummarySerializer

class KeySkillsViewSet(BaseViewSet):
    queryset = KeySkills.objects.all()
    serializer_class = KeySkillsSerializer

class EducationViewSet(BaseViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer

class ExperienceViewSet(BaseViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer

class ProjectViewSet(BaseViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class PersonalDetailsViewSet(BaseViewSet):
    queryset = PersonalDetails.objects.all()
    serializer_class = PersonalDetailsSerializer

class AddLinkViewSet(BaseViewSet):
    queryset = AddLink.objects.all()
    serializer_class = AddLinkSerializer

class LanguageViewSet(BaseViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

class ResumeViewSet(BaseViewSet):
    queryset = ResumeLink.objects.all()
    serializer_class = ResumeSerializer