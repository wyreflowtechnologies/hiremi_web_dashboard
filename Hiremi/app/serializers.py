from rest_framework import serializers
from .models import *

# ======================================================================================== #

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields = '__all__'

# ======================================================================================== #

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)

# ======================================================================================== #
class PercentageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Percentage
        fields = ['percentage']
# ======================================================================================== #

class ScoreCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreCard
        fields = '__all__'
        read_only_fields = ['id', 'average_score_stars']
# ======================================================================================== #

class FresherJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = FresherJob
        fields = '__all__'

# ======================================================================================== #

class ExperienceJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperienceJob
        fields = '__all__'

# ======================================================================================== #

class InternshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internship
        fields = '__all__'

# ======================================================================================== #

class VerificationDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationDetails
        fields = '__all__'

# ======================================================================================== #

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

# ======================================================================================== #

class OTPValidationSerializer(serializers.Serializer):
    otp = serializers.IntegerField()

# ======================================================================================== #

class ResetAccountPasswordSerializer(serializers.Serializer):
    pass1 = serializers.CharField(max_length=16)
    pass2 = serializers.CharField(max_length=16)

    def validate(self, data):
        if data['pass1'] != data['pass2']:
            raise serializers.ValidationError("Passwords do not match")
        return data

# ======================================================================================== #

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'

# ======================================================================================== #

class ExperienceJobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperienceJobApplication
        fields = '__all__'

# ======================================================================================== #

class InternshipApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternshipApplication
        fields = '__all__'

# ======================================================================================== #

# ======================================================================================== #

class MentorshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mentorship
        fields = '__all__'

# ======================================================================================== #

class CorporateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporateTraining
        fields = '__all__'

# ======================================================================================== #

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'

# ======================================================================================== #

class MentorshipDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorshipDiscount
        fields = '__all__'

# ======================================================================================== #

class CorporateDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporateDiscount
        fields = '__all__'

# ======================================================================================== #

class PaymentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    

# ======================================================================================== #

class CallbackSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        # Dynamically add fields based on the incoming data
        data = kwargs.get('data', {})
        super().__init__(*args, **kwargs)
        for field in data.keys():
            self.fields[field] = serializers.CharField(required=False, allow_blank=True)
    
    def create(self, validated_data):
        return PaymentTransaction.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.message = validated_data.get('message', instance.message)
        instance.txn_token = validated_data.get('txnToken', instance.txn_token)
        instance.save()
        return instance

# ======================================================================================== #

class TransactionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = '__all__'

# ======================================================================================== #

class TrainingProgramSerializer(serializers.ModelSerializer):
    
    discounted_price = serializers.ReadOnlyField()

    class Meta:
        model = TrainingProgram
        fields = '__all__' 

        
# ======================================================================================== #


class TrainingProgramApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingProgramApplication
        fields ='__all__' 

# ========================================================================================= #

class OrderStatusSerializer(serializers.Serializer):
    order_id = serializers.CharField(max_length=50)

# ========================================================================================= #

class OrderStatusResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusResponse
        fields = '__all__'




class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = '__all__'




class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class BasicDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicDetails
        fields = '__all__'

class ProfileSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileSummary
        fields = '__all__'

class KeySkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeySkills
        fields = '__all__'

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class PersonalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDetails
        fields = '__all__'

class AddLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddLink
        fields = '__all__'

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeLink
        fields = '__all__'