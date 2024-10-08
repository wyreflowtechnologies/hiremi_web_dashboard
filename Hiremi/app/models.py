from decimal import Decimal
from django.db import models, transaction
from django.core.validators import *
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Max
import random,re

# ======================================================================================== #

class BaseModel(models.Model):
    
    PAYMENT_STATUS_CHOICES = (
        ('Not Enroll', 'Not Enroll'),
        ('Enroll Pending', 'Enroll Pending'),
        ('Enrolled', 'Enrolled'),
    )

    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='Not Enroll')
    time_end = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.time_end = timezone.now()
        super().save(*args, **kwargs)


class Register(BaseModel):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    unique = models.CharField(max_length=8, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=300)
    father_name = models.CharField(max_length=300)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(unique=True,max_length=15, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')])
    whatsapp_number = models.CharField(unique=True,max_length=15, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')])
    college_state = models.CharField(max_length=100)
    birth_place = models.CharField(max_length=100, null=True)
    college_name = models.CharField(max_length=300)
    branch_name = models.CharField(max_length=200)
    degree_name = models.CharField(max_length=200, default='')
    passing_year = models.PositiveIntegerField()
    password = models.CharField(max_length=128, validators=[MinLengthValidator(8)])
    verified = models.BooleanField(default=False)
    otp = models.IntegerField(validators=[MaxValueValidator(999999), MinValueValidator(100000)], blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.unique:
            self.unique = self.generate_unique_number()
        # Hash the password before saving
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def generate_unique_number(self):
        try:
            with transaction.atomic():
                last_entry = Register.objects.select_for_update().order_by('-id').first()
                if last_entry and last_entry.unique:
                    last_number = int(last_entry.unique) + 1
                else:
                    last_number = 1
                return f"{last_number:08d}"
        except Exception as e:
            # Handle any error occurred during unique number generation
            raise ValidationError("Error generating unique number")

    def __str__(self):
        return self.full_name

    @classmethod
    def get_by_unique(cls, unique):
        return cls.objects.get(unique=unique)

    def get_related_objects(self):
        related_objects = {}
        for field in self._meta.related_objects:
            related_name = field.get_accessor_name()
            related_objects[related_name] = getattr(self, related_name).all()
        return related_objects
        
    class Meta:
        verbose_name = "Register"
        verbose_name_plural = "Registers"        

# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #

class JobInternshipBase(models.Model):
    """
    Abstract base model for job and internship positions.
    """
    YES_NO_CHOICES = (
        ('Yes', 'Yes'),
        ('No', 'No'),
    )
    ENVIRONMENT = [
        ('On-Site','On-Site'),
        ('Hybrid' , 'Hybrid'),
        ('Remote' , 'Remote'),
    ]

    profile = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    # code_required = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    # code = models.PositiveIntegerField(blank=True, null=True)
    work_environment = models.CharField(max_length=50, choices=ENVIRONMENT)
    company_name = models.CharField(max_length=255)
    education = models.CharField(max_length=255)
    skills_required = models.CharField(max_length=255)
    # knowledge_stars = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(5)])
    who_can_apply = models.CharField(max_length=255)
    description = models.TextField()
    # terms_and_conditions = models.TextField()
    about_company = models.TextField()
    years_experience_required = models.IntegerField(default=1)
    upload_date = models.DateTimeField(auto_now_add=True,null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.profile

    def clean(self):
        """
        Custom validation logic.
        """
        # if self.code_required == 'Yes' and not self.code:
        #     raise ValueError(_("Code is required when code_required is 'Yes'"))
        # if self.code and (self.code < 100 or self.code > 999):
        #     raise ValueError(_("Code must be a 3-digit number"))
        pass

    def save(self, *args, **kwargs):
        """
        Override the save method to add custom validation and ensure atomicity.
        """
        try:
            self.clean()  # Call the custom validation method
            with transaction.atomic():
                super().save(*args, **kwargs)
        except Exception as e:
            raise ValueError(f"Error saving {self.__class__.__name__}: {str(e)}")


class FresherJob(JobInternshipBase):
    """
    Model for fresher job positions.
    """
    CTC = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        verbose_name = "Fresher Job"
        verbose_name_plural = "Fresher Jobs"


class ExperienceJob(JobInternshipBase):
    """
    Model for Experience job positions.
    """
    
    CTC = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        verbose_name = "Experience Job"
        verbose_name_plural = "Experience Jobs"

class Internship(JobInternshipBase):
    """
    Model for internship positions.
    """
    Stipend = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()
    benifits = models.CharField(max_length=255)
    class Meta:
        verbose_name = "Internship"
        verbose_name_plural = "Internships"

# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #



class ApplicationBase(models.Model):
    STATUS_CHOICES = (
        ('Applied', 'Applied'),
        ('Select', 'Select'),
        ('Shortlisted', 'Shortlisted'),
        ('Reject', 'Reject'),
    )
    YEAR_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('Pass Out' , 'Pass Out'),
    )

    register = models.ForeignKey('Register', on_delete=models.CASCADE, related_name="%(class)ss")
    candidate_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    current_year = models.CharField(max_length=20, choices=YEAR_CHOICES ,default=1)
    applied_date = models.DateTimeField(auto_now_add=True,null=True)
    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.register.email} - {self.profile}"

    def clean(self):
        # Custom validation logic
        if self.candidate_status not in dict(self.STATUS_CHOICES):
            raise ValidationError(_('Invalid candidate status.'))

    def save(self, *args, **kwargs):
        self.clean()
        with transaction.atomic():
            super().save(*args, **kwargs)

    @classmethod
    def get_by_unique(cls, unique):
        try:
            register = Register.get_by_unique(unique)
            return cls.objects.filter(register=register)
        except Register.DoesNotExist:
            raise ValidationError(_('Register with unique ID does not exist.'))

class JobApplication(ApplicationBase):
    fresherjob = models.ForeignKey('FresherJob', on_delete=models.CASCADE, related_name="%(class)ss")

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"


class ExperienceJobApplication(ApplicationBase):
    experiencejob = models.ForeignKey('ExperienceJob', on_delete=models.CASCADE, related_name="%(class)ss")
    class Meta:
        verbose_name = "Experience Job Application"
        verbose_name_plural = "Experience Job Applications"

class InternshipApplication(ApplicationBase):
    internship = models.ForeignKey('Internship', on_delete=models.CASCADE, related_name="%(class)ss")

    class Meta:
        verbose_name = "Internship Application"
        verbose_name_plural = "Internship Applications"


# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #



class VerificationDetails(BaseModel):
    register = models.ForeignKey(Register, on_delete=models.CASCADE, related_name="verification_details")
    uid = models.CharField(max_length=8, unique=True, blank=True , null=True)
    college_id_number = models.CharField(max_length=20, unique=True, default='')
    interested_domain = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        try:
            with transaction.atomic():
                if self.payment_status == 'Enrolled' and not self.uid:
                    self.uid = self.generate_uid()
                elif self.payment_status != 'Enrolled':
                    raise ValidationError(_('Your payment is due. Please enroll first.'))
                super().save(*args, **kwargs)
        except Exception as e:
            raise ValidationError(_('Error saving VerificationDetails: %s') % e)

    def generate_uid(self):
        with transaction.atomic():
            last_uid = VerificationDetails.objects.filter(payment_status='Enrolled').aggregate(Max('uid'))['uid__max']
            last_number = int(last_uid[2:]) + 1 if last_uid else 1
            return f"HM{random.randint(0, 9999999999):10d}"

    def __str__(self):
        return f"VerificationDetails {self.college_id_number}"

    @classmethod
    def get_by_unique(cls, unique):
        try:
            register = Register.get_by_unique(unique)
            return cls.objects.filter(register=register)
        except Register.DoesNotExist:
            raise ValidationError(_('Register with unique ID does not exist.'))

    class Meta:
        verbose_name = "Verification Detail"
        verbose_name_plural = "Verification Details"




# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #

class MentorshipCorporateTrainingBase(BaseModel):
    STATUS_CHOICES = (
        ('Applied', 'Applied'),
        ('Select', 'Select'),
        ('Pending', 'Pending'),
        ('Reject', 'Reject'),
        ('EXPIRE', 'EXPIRE'),
        ('DirectSelect', 'DirectSelect'),
    )

    register = models.ForeignKey(Register, on_delete=models.CASCADE, related_name="%(class)ss")
    candidate_status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='Applied')
    applied = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} - {self.register.email}"

    def save(self, *args, **kwargs):
        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except Exception as e:
            raise ValidationError(f"Error saving {self.__class__.__name__}: {e}")

    @classmethod
    def get_by_unique(cls, unique):
        try:
            register = Register.get_by_unique(unique)
            return cls.objects.filter(register=register)
        except Register.DoesNotExist:
            raise ValidationError('Register with the given unique ID does not exist.')

class Mentorship(MentorshipCorporateTrainingBase):
    class Meta:
        verbose_name = "Mentorship"
        verbose_name_plural = "Mentorships"

class CorporateTraining(MentorshipCorporateTrainingBase):
    class Meta:
        verbose_name = "Corporate Training"
        verbose_name_plural = "Corporate Trainings"


# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #



class DiscountBase(models.Model):
    discount = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Discount as a percentage (0-100).")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)], help_text="Original price before discount.")

    class Meta:
        abstract = True

    def __str__(self):
        return f"Discount - {self.discount}%"

    def save(self, *args, **kwargs):
        try:
            with transaction.atomic():
                if not (0 <= self.discount <= 100):
                    raise ValidationError("Discount must be between 0 and 100 percent.")
                if self.original_price < 0:
                    raise ValidationError("Original price must be a positive value.")
                super().save(*args, **kwargs)
        except Exception as e:
            raise ValidationError(f"Error saving {self.__class__.__name__}: {e}")

class Discount(DiscountBase):
    class Meta:
        verbose_name = "Discount"
        verbose_name_plural = "Discounts"

class CorporateDiscount(DiscountBase):
    class Meta:
        verbose_name = "Corporate Discount"
        verbose_name_plural = "Corporate Discounts"

class MentorshipDiscount(DiscountBase):
    class Meta:
        verbose_name = "Mentorship Discount"
        verbose_name_plural = "Mentorship Discounts"



# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #


 

class TrainingProgram(models.Model):
    # register = models.ForeignKey(Register, on_delete=models.CASCADE, related_name="training_details", null=True)
    training_program = models.CharField(max_length=255)
    duration = models.CharField(max_length=255)
    original_price = models.PositiveIntegerField()
    discount_percentage = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Discount as a percentage (0-100).")
    upload_date = models.DateTimeField(auto_now_add=True,null=True)
    company_name = models.CharField(max_length=255,null=False, blank=False,)  # Add company name field
    training_description = models.TextField(null=False, blank=False)  # Add training description field
    skills_you_will_gain = models.TextField(null=False, blank=False)  # Add skills you will gain field
    What_you_Will_learm = models.TextField(null=False, blank=False)  # Add training description field
   

    @property
    def discounted_price(self):
        discount_amount = (Decimal(self.discount_percentage) / Decimal(100)) * self.original_price
        return self.original_price - discount_amount

    def clean(self):
        super().clean()
        # Ensure discount is between 0 and 100
        if not (0 <= self.discount_percentage <= 100):
            raise ValidationError("Discount percentage must be between 0 and 100.")

    def __str__(self):
        return self.training_program


# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #

class TrainingProgramApplication(BaseModel):
    applied = [
        ('Applied', 'Applied'),
        ('Not Applied', 'Not Applied'),
    ]
    register = models.ForeignKey(Register, on_delete=models.CASCADE, related_name="training_details", null=True)
    TrainingProgram = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE,related_name="training_details", null=True)
#    // upload_date = models.DateTimeField(auto_now_add=True,null=True)
    applied = models.CharField(max_length=20, choices=applied, default='Not Applied')
    

    def __str__(self):
        return f"{self.register} - {self.TrainingProgram} ({self.applied})"
  

# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #


class PaymentTransaction(models.Model):

    email = models.EmailField()  # Ensure this field exists if using email for identification
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], help_text="Amount in currency.")
    txn_token = models.CharField(max_length=100)
    order_id = models.CharField(max_length=100, unique=True, help_text="Unique identifier for the transaction.")
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    @classmethod
    def get_by_unique(cls, unique):
        register = Register.get_by_unique(unique)
        return cls.objects.filter(register=register)

    def _str_(self):
        return f"Payment of {self.amount} made at {self.created_at}"        

# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
    

class OrderStatusResponse(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    txn_id = models.CharField(max_length=100, null=True, blank=True)
    result_msg = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_by_unique(cls, unique):
        try:
            register = Register.get_by_unique(unique)
            return cls.objects.filter(register=register)
        except Exception as e:
            raise ValidationError(f"Error retrieving OrderStatusResponse: {e}")
        


class Percentage(models.Model):
    percentage = models.IntegerField()

# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #
# ======================================================================================== #    



class ScoreCard(models.Model):
    register = models.ForeignKey(Register, on_delete=models.CASCADE, related_name="scorecards")
    profile = models.CharField(max_length=255)
    scores = models.JSONField()  # Use the built-in JSONField
    average_score_stars = models.PositiveIntegerField(default=0)  # Field to store average score in stars

    def __str__(self):
        return f"ScoreCard for {self.register.full_name}"
    
    @classmethod
    def get_by_unique(cls, unique):
        try:
            register = Register.get_by_unique(unique)
            return cls.objects.filter(register=register)
        except Register.DoesNotExist:
            raise ValidationError(_('Register with unique ID does not exist.'))

    def calculate_average_score(self):
        total_score = sum(self.scores.values())
        num_scores = len(self.scores)
        if num_scores > 0:
            average_score = total_score / num_scores
            return average_score
        return 0

    def convert_to_stars(self):
        average_score = self.calculate_average_score()
        # Assuming the stars range from 1 to 5 based on the average score
        stars = round(average_score / 20)  # Dividing by 20 because 100 / 5 = 20
        return stars

    def save(self, *args, **kwargs):
        self.average_score_stars = self.convert_to_stars()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "ScoreCard"
        verbose_name_plural = "ScoreCards"





class Query(models.Model):
    ISSUE_CHOICES = [
        ('general', 'General Inquiry'),
        ('technical', 'Technical Issue'),
        ('billing', 'Billing Issue'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    register = models.ForeignKey('Register', on_delete=models.CASCADE, related_name="queries")
    name = models.CharField(
        max_length=100, 
        validators=[
            MinLengthValidator(2, message="Name must be at least 2 characters long.")
        ]
    )
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    issue = models.CharField(max_length=50, choices=ISSUE_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.issue}"

    def save(self, *args, **kwargs):
        # Add any custom save behavior here if needed
        super(Query, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]

class Profile(models.Model):
    register = models.OneToOneField('Register', on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.register.full_name}"

    def clean(self):
        # Add custom validation logic if needed
        pass

class BasicDetails(models.Model):
    LOOKING_FOR = [
        ('Internships', 'Internships'),
        ('Fresher Job', 'Fresher Jobs'),
        ('Experienced', 'Experienced Jobs'),
    ]
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='basic_details')
    looking_for = models.CharField(max_length=50, choices=LOOKING_FOR)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_("Enter a valid phone number."))]
    )
    whatsapp_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_("Enter a valid phone number."))]
    )
    def __str__(self):
        return f"Basic Details of {self.profile.register.full_name}"

    def clean(self):
        if not self.first_name or not self.last_name:
            raise ValidationError(_("First name and last name cannot be empty."))

class ProfileSummary(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='profile_summary')
    summary = models.TextField()

    def __str__(self):
        return f"Profile Summary of {self.profile.register.full_name}"

    def clean(self):
        if not self.summary:
            raise ValidationError(_("Summary cannot be empty."))

class KeySkills(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='key_skills')
    skill = models.CharField(max_length=100)

    def __str__(self):
        return f"Key Skill {self.skill} of {self.profile.register.full_name}"

    def clean(self):
        if not self.skill:
            raise ValidationError(_("Skill cannot be empty."))

class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education')
    education = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    marks = models.BigIntegerField()
    passing_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900, message=_("Passing year cannot be before 1900.")),
            MaxValueValidator(timezone.now().year+30, message=_("Passing year cannot be in the future."))
        ]
    )

    def __str__(self):
        return f"Education {self.degree} of {self.profile.register.full_name}"

    def clean(self):
        if not self.degree or not self.institution:
            raise ValidationError(_("Degree and institution cannot be empty."))

class Experience(models.Model):
    WORK_EXPERIENCE = [
        ('YES','YES'),
        ('NO' , 'NO'),
    ]
    WORK_ENVIRONMENT = [
        ('On-Site','On-Site'),
        ('Hybrid' , 'Hybrid'),
        ('Remote' , 'Remote'),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experience')
    work_experience = models.CharField(max_length=50, choices=WORK_EXPERIENCE)
    work_environment = models.CharField(max_length=50, choices=WORK_ENVIRONMENT)
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=100)
    skill_used = models.CharField(max_length=100,null=True)
    start_date = models.DateField()
    current_company = models.CharField(max_length=50, choices=WORK_EXPERIENCE)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Experience {self.job_title} of {self.profile.register.full_name}"

    def clean(self):
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError(_("End date cannot be before start date."))

class Project(models.Model):
    STATUS = [
        ('Completed','Completed'),
        ('On-Going','On-Going'),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='projects')
    project_title = models.CharField(max_length=200)
    client = models.CharField(max_length=200)
    link = models.URLField(null=True, blank=True, validators=[URLValidator()])
    start_date = models.DateField()
    status = models.CharField(max_length=20,choices=STATUS)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f"Project {self.project_name} of {self.profile.register.full_name}"

    def clean(self):
        if not self.project_name:
            raise ValidationError(_("Project name cannot be empty."))
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError(_("End date cannot be before start date."))

class PersonalDetails(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='personal_details')
    gender = models.CharField(max_length=10, choices=(('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')))
    marital_status = models.CharField(max_length=10, choices=(('Single', 'Single'), ('Married', 'Married'), ('Other', 'Other')))
    home_town = models.CharField(max_length=100)
    pincode = models.IntegerField()
    local_address = models.CharField(max_length=100)
    permanent_address = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    ability = models.CharField(max_length=10, choices=(('Yes', 'Yes'), ('No', 'No')))
    category = models.CharField(max_length=10)

    def __str__(self):
        return f"Personal Details of {self.profile.register.full_name}"

    def clean(self):
        if not self.date_of_birth or not self.gender or not self.nationality:
            raise ValidationError(_("Date of birth, gender, and nationality cannot be empty."))

class AddLink(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='links')
    linkedin_url = models.URLField(
        null=True, 
        blank=True, 
        validators=[URLValidator()],
        help_text="Enter LinkedIn profile URL."
    )
    github_url = models.URLField(
        null=True, 
        blank=True, 
        validators=[URLValidator()],
        help_text="Enter GitHub profile URL."
    )
    Portfolio = models.URLField(
        null=True, 
        blank=True, 
        validators=[URLValidator()],
        help_text="Enter Portfolio profile URL."
    )
    Others = models.URLField(
        null=True, 
        blank=True, 
        validators=[URLValidator()],
        help_text="Enter Others profile URL."
    )

    def __str__(self):
        linkedin_str = f"LinkedIn: {self.linkedin_url}" if self.linkedin_url else "No LinkedIn URL"
        github_str = f"GitHub: {self.github_url}" if self.github_url else "No GitHub URL"
        return f"{linkedin_str}, {github_str} for {self.profile.register.full_name}"

    def clean(self):
        # Ensure at least one URL is provided
        if not self.linkedin_url and not self.github_url:
            raise ValidationError("At least one URL (LinkedIn or GitHub) must be provided.")

class ResumeLink(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='resume')
    url = models.URLField(validators=[URLValidator()])

    def __str__(self):
        return f"Resume of {self.profile.register.full_name}"


class Language(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='languages')
    language = models.CharField(max_length=100)

    def __str__(self):
        return f"Language {self.language} of {self.profile.register.full_name}"

    def clean(self):
        if not self.language:
            raise ValidationError("Language cannot be empty.") 