from django.shortcuts import render,redirect
from django.contrib.auth import  login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
import random
import requests
from django.core.mail import send_mail
from django.core.paginator import Paginator
from datetime import datetime
from operator import itemgetter
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt
# =======================================================================================================
# =======================================================================================================
# @login_required(login_url='/superuser_login/')
def index(request):
    return render(request, 'index.html')


def otp_page(request):
    return render(request, 'otp-page.html')

# @login_required
def superuser_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('superuser_login')

@csrf_exempt
def superuser_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        print(email, password)

        if user is not None and user.is_superuser:
            # Generate a random OTP
            otp = random.randint(100000, 999999)
            
            # Save the OTP in the session
            request.session['otp'] = otp
            request.session['superuser_email'] = email

            # Send OTP to the superuser's email
            send_mail(
                'Your OTP for Login',
                f'Your OTP is {otp}',
                'hiremiotp@gmail.com',  # Replace with your "from" email
                [email],
                fail_silently=False,
            )
            print(otp)

            # Redirect to OTP verification page
            return render(request, 'otp-page.html', {'email': email})
        else:
            # Handling invalid login attempts
            error = 'Invalid email or password for superuser.'
            return render(request, 'index.html', {'error': error, 'email': email})
    
    return render(request, 'index.html')


def otp_verify(request):
    if request.method == 'POST':
        print("hiii")
        otp_digits = [
            request.POST.get('digit1'),
            request.POST.get('digit2'),
            request.POST.get('digit3'),
            request.POST.get('digit4'),
            request.POST.get('digit5'),
            request.POST.get('digit6')
        ]
        print(otp_digits)
        entered_otp = ''.join(otp_digits)
        session_otp = str(request.session.get('otp'))

        if entered_otp == session_otp:
            email = request.session.get('superuser_email')
            user = authenticate(request, username=email, password="admin")

            if user is not None:
                login(request, user)
                # Clean up session data
                del request.session['otp']
                del request.session['superuser_email']

                # Redirect to the dashboard instead of rendering directly
                return redirect('dashboard')  # Update with your actual dashboard URL or name
            else:
                messages.error(request, 'Unable to authenticate. Please try again.')
        else:
            # OTP is incorrect
            messages.error(request, 'Invalid OTP. Please try again.')

    # If OTP is incorrect or request method is GET
    return render(request, 'otp-page.html',{'email':email})




def resend_otp(request):
    if 'superuser_email' in request.session:
        email = request.session['superuser_email']  
        otp = random.randint(100000, 999999) 
        print(email)
        request.session['otp'] = otp
        send_mail(
            'Your Resent OTP for Login',
            f'Your OTP is {otp}',
            'hiremiotp@gmail.com',
            [email],
            fail_silently=False,
        )
        print(f"Resent OTP: {otp}")
        messages.success(request, 'A new OTP has been sent to your email.')
        return redirect('otp_page') 
    messages.error(request, 'Unable to resend OTP. Please try logging in again.')
    return redirect('superuser_login')  




# ============================================================================================================
# ============================================================================================================


#                                           Dashboard Section Started
# ============================================================================================================
# ============================================================================================================


INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Delhi"
]


INTERESTED_DOMAINS = [
    'Website Development', 'MERN Development', 'Software Development',
    'Frontend Development', 'Backend Development', 'Flutter UI Development',
    'Java Development', 'Finance Management', 'Marketing Management',
    'Human Resource Management', 'Operations Management', 'Business Analytics',
    'International Business', 'Supply Chain Management'
]

DEGREES = [
    'B.Com', 'B.Sc', 'B.Tech', 'BBA', 'BCA', 'Diploma',
    'M.Com', 'M.Sc', 'M.Tech', 'MBA', 'MCA', 'Other'
]


BRANCHES = [
    'Aerospace Engineering', 'Automotive Engineering', 'Chemical Engineering',
    'Civil Engineering', 'Computer Science and Engineering', 'Electrical Engineering',
    'Electronics and Communication Engineering', 'Finance', 'Human Resources',
    'Industrial Engineering', 'Information Technology', 'Marine Engineering',
    'Marketing', 'Materials Engineering', 'Mechanical Engineering',
    'Metallurgical Engineering', 'Nuclear Engineering', 'Robotics Engineering',
    'Sales', 'Other'
]

BASE_API_URL = 'http://13.127.246.196:8000'


registrations_url = f'{BASE_API_URL}/api/registers/'
queries_url = f'{BASE_API_URL}/api/queries/'
verification_url = f'{BASE_API_URL}/api/verification-details/'
internship_application_url = f'{BASE_API_URL}/api/internship-applications/'
internship_url=f'{BASE_API_URL}/api/internship/'
fresher_Job_url=f'{BASE_API_URL}/api/fresherjob/'
experience_Job_url=f'{BASE_API_URL}//api/experiencejob/'
corporate_training_url=f'{BASE_API_URL}/api/corporatetraining/'




# ===================================== F U N T I O N S ========================================== #

def count_verified_users_from_api(api_url, sort_by='verified'):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Initialize counters
        verified_count = sum(1 for user in data if user['verified'])
        non_verified_count = sum(1 for user in data if not user['verified'])
        male_verified_count = sum(1 for user in data if user['gender'] == 'Male' and user['verified'])
        male_non_verified_count = sum(1 for user in data if user['gender'] == 'Male' and not user['verified'])
        female_verified_count = sum(1 for user in data if user['gender'] == 'Female' and user['verified'])
        female_non_verified_count = sum(1 for user in data if user['gender'] == 'Female' and not user['verified'])
        total_male_count = sum(1 for user in data if user['gender'] == 'Male')
        total_female_count = sum(1 for user in data if user['gender'] == 'Female')
        
        birth_place_data = {state: {'registered': 0, 'verified': 0, 'non_verified': 0} for state in INDIAN_STATES}
        
        # Loop through each user and update the counts based on their birth place and verification status
        for user in data:
            birth_place = user.get('birth_place', None)
            if birth_place in birth_place_data:
                birth_place_data[birth_place]['registered'] += 1
                if user['verified']:
                    birth_place_data[birth_place]['verified'] += 1
                else:
                    birth_place_data[birth_place]['non_verified'] += 1
        
        # Sort birth place data
        if sort_by == 'verified':
            sorted_data = dict(sorted(birth_place_data.items(), key=lambda item: item[1]['verified'], reverse=True))
        elif sort_by == 'non_verified':
            sorted_data = dict(sorted(birth_place_data.items(), key=lambda item: item[1]['non_verified'], reverse=True))
        elif sort_by == 'registered':
            sorted_data = dict(sorted(birth_place_data.items(), key=lambda item: item[1]['registered'], reverse=True))
        elif sort_by == 'alphabetical':
            sorted_data = dict(sorted(birth_place_data.items(), key=lambda item: item[0].lower()))
        else:
            sorted_data = birth_place_data
        
        return {
            'verified_count': verified_count,
            'non_verified_count': non_verified_count,
            'male_verified_count': male_verified_count,
            'male_non_verified_count': male_non_verified_count,
            'female_verified_count': female_verified_count,
            'female_non_verified_count': female_non_verified_count,
            'total_male_count': total_male_count,
            'total_female_count': total_female_count,
            'birth_place_data': sorted_data  # Return sorted birth place data
        }
    
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return {
            'verified_count': 0,
            'non_verified_count': 0,
            'male_verified_count': 0,
            'male_non_verified_count': 0,
            'female_verified_count': 0,
            'female_non_verified_count': 0,
            'total_male_count': 0,
            'total_female_count': 0,
            'birth_place_data': {state: {'registered': 0, 'verified': 0, 'non_verified': 0} for state in INDIAN_STATES}
        }

        
def count_queries_from_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Initialize counters
        total_queries_count = len(data)
        closed_queries_count = sum(1 for query in data if query['status'] == 'closed')
        open_queries_count = total_queries_count - closed_queries_count  # or sum(1 for query in data if query['status'] == 'open')

        return {
            'total_queries_count': total_queries_count,
            'closed_queries_count': closed_queries_count,
            'open_queries_count': open_queries_count,
        }
    
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return {
            'total_queries_count': 0,
            'closed_queries_count': 0,
            'open_queries_count': 0,
        }        

# ================================================================================================= #





# -------------------------------------------------------------------------------------------------------------------------------------------------- #








""" =====================================               D A S H B O A R D  &  S E C T I O N S              ======================================== """
import pytz
from django.utils import timezone
from django.http import HttpResponse
# @login_required
def dashboard(request):
    try:
        # Get user counts from the API
        user_counts = count_verified_users_from_api(registrations_url)
        query_counts = count_queries_from_api(queries_url)
        
        # Fetch the full list of registrations
        response = requests.get(registrations_url)
        response.raise_for_status()
        data = response.json()
        user_count = len(data)

        # Fetch other data (internship, fresher jobs, experienced jobs)
        internship = requests.get(internship_url).json()
        intern_count = len(internship)

        fresher_data = requests.get(fresher_Job_url).json()
        fresher_count = len(fresher_data)

        experience_data = requests.get(experience_Job_url).json()
        experience_count = len(experience_data)

        # Handle last login conversion to IST
        last_login = 'N/A'
        if request.user.is_authenticated:
            last_login = request.user.last_login
            if last_login:
                # Ensure last_login is treated as UTC if naive
                if timezone.is_naive(last_login):
                    last_login = timezone.make_aware(last_login, timezone.utc)
                
                # Convert to IST
                ist_timezone = pytz.timezone('Asia/Kolkata')
                last_login = last_login.astimezone(ist_timezone)
                
                # Format the date and time in IST
                last_login = last_login.strftime('%A, %d %B, %Y %I:%M:%S %p')  # 12-hour clock with AM/PM

    except requests.exceptions.RequestException as e:
        # Handle API errors gracefully
        return HttpResponse(f"An error occurred while fetching data: {e}", status=500)
    
# this is used to count the total register in this month
# -------------------------------------------------------
    url = "http://13.127.246.196:8000/api/registers/"

    current_year = datetime.now().year
    current_month = datetime.now().month
    params = {
        'created_at__year': current_year,
        'created_at__month': current_month,
    }
    response = requests.get(url, params=params)
    total_registrations = 0

    if response.status_code == 200:
        data = response.json()
        total_registrations = len(data)

# ----------------------------------------------------------
    url = "http://13.127.246.196:8000/api/registers/"

    current_year = datetime.now().year
    current_month = datetime.now().month
    params = {
        # 'created_at__year': current_year,
        # 'created_at__month': current_month,
         'verified': True, 
    }
    response = requests.get(url, params=params)
    total_verified = 0

    if response.status_code == 200:
        data = response.json()
        total_verified = len(data)

# -----------------------------------------------------------
    url = "http://13.127.246.196:8000/api/registers/"

    current_year = datetime.now().year
    current_month = datetime.now().month
    params = {
        # 'created_at__year': current_year,
        # 'created_at__month': current_month,
         'verified': False, 
    }
    response = requests.get(url, params=params)
    total_not_verified = 0

    if response.status_code == 200:
        data = response.json()
        total_not_verified = len(data)   
        
    context = {
        'user_count': user_count,
        'verified_count': user_counts['verified_count'],
        'non_verified_count': user_counts['non_verified_count'],
        'male_verified_count': user_counts['male_verified_count'],
        'male_non_verified_count': user_counts['male_non_verified_count'],
        'female_verified_count': user_counts['female_verified_count'],
        'female_non_verified_count': user_counts['female_non_verified_count'],
        'total_male_count': user_counts['total_male_count'],
        'total_female_count': user_counts['total_female_count'],
        'total_queries_count': query_counts['total_queries_count'],
        'closed_queries_count': query_counts['closed_queries_count'],
        'open_queries_count': query_counts['open_queries_count'],
        'intern_count': intern_count,
        'fresher_count': fresher_count,
        'experience_count': experience_count,
        'last_login': last_login,
        'total_registrations':total_registrations,
        'total_verified':total_verified ,
        'total_not_verified':total_not_verified,
    }
    
    return render(request, "dashboard/dashboard.html", context)


from django.shortcuts import render, get_object_or_404
import requests
BASE_URL = "http://13.127.246.196:8000/api/"

def fetch_and_filter(endpoint, identifier, key='profile'):
    """Helper function to fetch and filter data from an API endpoint."""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        response.raise_for_status()
        data = response.json()
        return next((item for item in data if item[key] == identifier), None)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        return None

# def view_user(request, pk):
#     context = {}

#     try:
#         # Fetch the register object using the primary key (pk)
#         register_response = requests.get(f"{BASE_URL}registers/{pk}/")
#         register_response.raise_for_status()
#         register_data = register_response.json()
#         register_id = register_data.get('id')

#         if not register_id:
#             print(f"Register ID not found for pk: {pk}")
#             return render(request, 'error.html', {'error': 'Register not found'})

#         print(f"Register ID: {register_id}")
#         context['register'] = register_data

#         # Fetch the profile matching the register ID
#         profile = fetch_and_filter("profiles/", register_id, key='register')
#         verification_details = fetch_and_filter("verification-details/", register_id, key='register')
        
#         if verification_details:
#             context['verification_details'] = verification_details

#         if profile:
#             profile_id = profile.get('id')
#             print(f"Profile ID: {profile_id}")
#             context['profile'] = profile

#             # Fetch and filter data from various endpoints
#             basic_details = fetch_and_filter("basic-details/", profile_id)
#             personal_details = fetch_and_filter("personal-details/", profile_id)
#             profile_summary = fetch_and_filter("profile-summaries/", profile_id)
#             key_skills = fetch_and_filter("key-skills/", profile_id)
#             education = fetch_and_filter("education/", profile_id)
#             experience = fetch_and_filter("experiences/", profile_id)
#             projects = fetch_and_filter("projects/", profile_id)
#             links = fetch_and_filter("links/", profile_id)
#             languages = fetch_and_filter("languages/", profile_id, key='profile')
#             resumelink = fetch_and_filter("resumelink/", profile_id)

            

#             # Add data to context only if it's successfully fetched
#             if basic_details:
#                 context['basic_details'] = basic_details
#             if personal_details:
#                 context['personal_details'] = personal_details
#             if profile_summary:
#                 context['profile_summary'] = profile_summary
#             if key_skills:
#                 skills_list = [skill.strip() for skill in key_skills.get('skill', '').split(',')] if key_skills else []
#                 context['key_skills'] = skills_list
#             if education:
#                 context['education'] = education
#             if experience:
#                 context['experience'] = experience
#             if projects:
#                 context['projects'] = projects
#             if links:
#                 context['links'] = links
#             if languages:
#                 language_list = [language.strip() for language in languages.get('language', '').split(',')] if languages else []
#                 context['languages'] = language_list
#             if resumelink:
#                 context['resumelink'] = resumelink

#         else:
#             print(f"No profile found for register ID: {register_id}")
            
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching register or profiles: {e}")
#         context['error'] = 'An error occurred while fetching data.'

#     print(context)
#     return render(request, 'view-user.html', context)



def delete_user(request, pk):
    # URL of the API endpoint
    url = f"http://13.127.246.196:8000/api/registers/{pk}/"
    
    # Perform the DELETE request
    response = requests.delete(url)
    
    if response.status_code == 204:
        # Successfully deleted
        return redirect('total_user')  # Redirect to 'total_user' view (change to your actual view name or URL)
    else:
        # Failed to delete, handle the error
        return HttpResponse("Error deleting user", status=response.status_code)
    


def view_user(request, pk):
    context = {}

    try:
        # Fetch the register object using the primary key (pk)
        register_response = requests.get(f"{BASE_URL}registers/{pk}/")
        register_response.raise_for_status()
        register_data = register_response.json()
        register_id = register_data.get('id')

        if not register_id:
            print(f"Register ID not found for pk: {pk}")
            return render(request, 'error.html', {'error': 'Register not found'})

        print(f"Register ID: {register_id}")
        
        # Handle time_end field in the register data
        time_end_str = register_data.get("time_end")
        if time_end_str:
            try:
                # Convert string to datetime object in UTC
                utc_datetime = datetime.strptime(time_end_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                # Localize datetime to UTC
                utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)
                # Convert UTC to IST
                ist_timezone = pytz.timezone('Asia/Kolkata')
                ist_datetime = utc_datetime.astimezone(ist_timezone)
                # Extract the date part
                register_data["time_end"] = ist_datetime.date()
            except ValueError as e:
                # Handle any potential errors in parsing the datetime
                register_data["time_end"] = f"Error parsing date: {e}"
        else:
            register_data["time_end"] = "--"

        context['register'] = register_data

        # Fetch the profile matching the register ID
        profile = fetch_and_filter("profiles/", register_id, key='register')
        verification_details = fetch_and_filter("verification-details/", register_id, key='register')

        # Handle time_end field in verification_details
        if verification_details:
            time_end_str = verification_details.get("time_end")
            if time_end_str:
                try:
                    # Convert string to datetime object in UTC
                    utc_datetime = datetime.strptime(time_end_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    # Localize datetime to UTC
                    utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)
                    # Convert UTC to IST
                    ist_timezone = pytz.timezone('Asia/Kolkata')
                    ist_datetime = utc_datetime.astimezone(ist_timezone)
                    # Extract the date part
                    verification_details["time_end"] = ist_datetime.date()
                except ValueError as e:
                    # Handle any potential errors in parsing the datetime
                    verification_details["time_end"] = f"Error parsing date: {e}"
            else:
                verification_details["time_end"] = "--"
            
            context['verification_details'] = verification_details

        if profile:
            profile_id = profile.get('id')
            print(f"Profile ID: {profile_id}")
            context['profile'] = profile

            # Fetch and filter data from various endpoints
            basic_details = fetch_and_filter("basic-details/", profile_id)
            personal_details = fetch_and_filter("personal-details/", profile_id)
            profile_summary = fetch_and_filter("profile-summaries/", profile_id)
            key_skills = fetch_and_filter("key-skills/", profile_id)
            education = fetch_and_filter("education()/", profile_id)
            experience = fetch_and_filter("experiences/", profile_id)
            projects = fetch_and_filter("projects/", profile_id)
            links = fetch_and_filter("links/", profile_id)
            languages = fetch_and_filter("languages/", profile_id, key='profile')
            resumelink = fetch_and_filter("resumelink/", profile_id)

            # Add data to context only if it's successfully fetched
            if basic_details:
                context['basic_details'] = basic_details
            if personal_details:
                context['personal_details'] = personal_details
            if profile_summary:
                context['profile_summary'] = profile_summary
            if key_skills:
                skills_list = [skill.strip() for skill in key_skills.get('skill', '').split(',')] if key_skills else []
                context['key_skills'] = skills_list
            if education:
                context['education'] = education
            if experience:
                context['experience'] = experience
            if projects:
                context['projects'] = projects
            if links:
                context['links'] = links
            if languages:
                language_list = [language.strip() for language in languages.get('language', '').split(',')] if languages else []
                context['languages'] = language_list
            if resumelink:
                context['resumelink'] = resumelink

        else:
            print(f"No profile found for register ID: {register_id}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching register or profiles: {e}")
        context['error'] = 'An error occurred while fetching data.'

    print(context)
    return render(request, 'view-user.html', context)
    
# =========================== C O M P L E T E D ==================================== #



def non_verified_female(request):

    try:
        # Fetch the user data from the API
        users_response = requests.get(registrations_url)
        users_response.raise_for_status()  # Raise an exception for HTTP errors
        users_data = users_response.json()

        # Filter the data to include only non-verified female users
        female_non_verified_users = [
            {
                'id': user.get('id','--'),
                'full_name': user.get('full_name', '--'),
                'email': user.get('email', '--'),
                'phone_number': user.get('phone_number', '--'),
                'gender': user.get('gender', '--'),
                'degree_name': user.get('degree_name', '--'),
                'birth_place': user.get('birth_place', '--'),
                'college_state': user.get('college_state', '--'),
                'passing_year': user.get('passing_year', '--'),
                'verified': 'Verified' if user.get('verified') else 'Not Verified'
            }
            for user in users_data if user.get('gender') == 'Female' and not user.get('verified')
        ]

        # Check if sorting is requested
        sort_by = request.GET.get('sort_by', '')

        if sort_by == 'name':
            female_non_verified_users.sort(key=lambda x: x['full_name'].lower())

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        # If there is an error, set female_non_verified_users to an empty list
        female_non_verified_users = []

    # Render the template with the filtered data
    return render(request, 'dashboard/non-verified-female.html', {'female_non_verified_users': female_non_verified_users})



def non_verified_male(request):
    try:
        # Fetch the user data from the API
        users_response = requests.get(registrations_url)
        users_response.raise_for_status()  # Raise an exception for HTTP errors
        users_data = users_response.json()

        # Filter the data to include only non-verified male users
        male_non_verified_users = [
            {
                'id': user.get('id','--'),
                'full_name': user.get('full_name', '--'),
                'email': user.get('email', '--'),
                'phone_number': user.get('phone_number', '--'),
                'gender': user.get('gender', '--'),
                'degree_name': user.get('degree_name', '--'),
                'birth_place': user.get('birth_place', '--'),
                'college_state': user.get('college_state', '--'),
                'passing_year': user.get('passing_year', '--'),
                'verified': 'Verified' if user.get('verified') else 'Not Verified'
            }
            for user in users_data if user.get('gender') == 'Male' and not user.get('verified')
        ]

        # Check if sorting is requested
        sort_by = request.GET.get('sort_by', '')

        if sort_by == 'name':
            male_non_verified_users.sort(key=lambda x: x['full_name'].lower())

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        # If there is an error, set male_non_verified_users to an empty list
        male_non_verified_users = []

    # Render the template with the filtered data
    return render(request, 'dashboard/non-verified-male.html', {'male_non_verified_users': male_non_verified_users})



def verified_male(request):
    
    try:
        # Fetch the user data from the API
        users_response = requests.get(registrations_url)
        users_response.raise_for_status()
        users_data = users_response.json()
        
        # Fetch the verification data from the API
        verification_response = requests.get(verification_url)
        verification_response.raise_for_status()
        verification_data = verification_response.json()
        
        # Create a mapping from user ID to UID
        uid_map = {item["register"]: item["uid"] for item in verification_data}
        
        # Filter the data to include only verified male users
        male_verified_users = [
            {    
                'id': user.get('id','--'),
                'uid': uid_map.get(user.get('id'), '--'),  # Get UID from the mapping
                'full_name': user.get('full_name', '--'),
                'email': user.get('email', '--'),
                'phone_number': user.get('phone_number', '--'),
                'gender': user.get('gender', '--'),
                'degree_name': user.get('degree_name', '--'),
                'birth_place': user.get('birth_place', '--'),
                'college_state': user.get('college_state', '--'),
                'passing_year': user.get('passing_year', '--'),
                'verified': 'Verified' if user.get('verified') else 'Not Verified',
            }
            for user in users_data if user.get('gender') == 'Male' and user.get('verified')
        ]
        sort_by = request.GET.get('sort_by', '')

        if sort_by == 'name':
            male_verified_users.sort(key=lambda x: x['full_name'].lower())

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        # If there is an error, set male_verified_users to an empty list
        male_verified_users = []

    # Render the template with the filtered data
    return render(request, 'dashboard/verified-male.html', {'male_verified_users': male_verified_users})



def verified_female(request):
    try:
        # Fetch the user data from the API
        users_response = requests.get(registrations_url)
        users_response.raise_for_status()
        users_data = users_response.json()

        # Fetch the verification data from the API
        verification_response = requests.get(verification_url)
        verification_response.raise_for_status()
        verification_data = verification_response.json()

        # Create a mapping from user ID to UID
        uid_map = {item["register"]: item["uid"] for item in verification_data}

        # Filter the data to include only verified female users
        female_verified_users = [
            {
                'id': user.get('id','--'),
                'uid': uid_map.get(user.get('id'), '--'),  # Get UID from the mapping
                'full_name': user.get('full_name', '--'),
                'email': user.get('email', '--'),
                'phone_number': user.get('phone_number', '--'),
                'gender': user.get('gender', '--'),
                'degree_name': user.get('degree_name', '--'),
                'birth_place': user.get('birth_place', '--'),
                'college_state': user.get('college_state', '--'),
                'passing_year': user.get('passing_year', '--'),
                'verified': 'Verified' if user.get('verified') else 'Not Verified'
            }
            for user in users_data if user.get('gender') == 'Female' and user.get('verified')
        ]

        sort_by = request.GET.get('sort_by', '')

        if sort_by == 'name':
            female_verified_users.sort(key=lambda x: x['full_name'].lower())

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        # If there is an error, set female_verified_users to an empty list
        female_verified_users = []

    # Render the template with the filtered data
    return render(request, 'dashboard/verified-female.html', {'female_verified_users': female_verified_users})



def interested_domain(request):

    try:
        response = requests.get(verification_url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return render(request, 'error.html', {'error': str(e)})

    # Initialize dictionaries to store counts by interested domain
    domain_summary = {domain: {'total': 0, 'verified': 0, 'non_verified': 0} for domain in INTERESTED_DOMAINS}

    # Process each record
    for record in data:
        interested_domain = record.get('interested_domain')
        verified = record.get('verified', False)

        # Update counts
        if interested_domain in domain_summary:
            domain_summary[interested_domain]['total'] += 1
            if verified:
                domain_summary[interested_domain]['verified'] += 1
            else:
                domain_summary[interested_domain]['non_verified'] += 1

    # Get sorting parameter from request
    sort_by = request.GET.get('sort_by', 'total')  # Default to sorting by total if no sort parameter is provided

    # Sort the result based on the selected sorting parameter
    if sort_by == 'non_verified':
        sorted_summary = dict(sorted(domain_summary.items(), key=lambda item: item[1]['non_verified'], reverse=True))
    elif sort_by == 'domain':
        sorted_summary = dict(sorted(domain_summary.items()))  # Default sorting by Domain
    else:
        sorted_summary = dict(sorted(domain_summary.items(), key=lambda item: item[1]['total'], reverse=True))

    return render(request, 'dashboard/interested-domain.html', {'domain_summary': sorted_summary})



def branch(request):
 
    try:
        response = requests.get(registrations_url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return render(request, 'error.html', {'error': str(e)})

    # Initialize dictionaries to store counts by branch
    branch_summary = {branch: {'total': 0, 'verified': 0, 'non_verified': 0} for branch in BRANCHES}

    # Process each record
    for record in data:
        branch = record.get('branch_name')
        verified = record.get('verified', False)

        # Update counts
        if branch in branch_summary:
            branch_summary[branch]['total'] += 1
            if verified:
                branch_summary[branch]['verified'] += 1
            else:
                branch_summary[branch]['non_verified'] += 1

    # Get sorting parameter from request
    sort_by = request.GET.get('sort_by', 'total')  # Default to sorting by total if no sort parameter is provided

    # Sort the result based on the selected sorting parameter
    if sort_by == 'verified':
        sorted_summary = dict(sorted(branch_summary.items(), key=lambda item: item[1]['verified'], reverse=True))
    elif sort_by == 'non_verified':
        sorted_summary = dict(sorted(branch_summary.items(), key=lambda item: item[1]['non_verified'], reverse=True))
    elif sort_by == 'branch':
        sorted_summary = dict(sorted(branch_summary.items()))  # Default sorting by Branch name
    else:
        sorted_summary = dict(sorted(branch_summary.items(), key=lambda item: item[1]['total'], reverse=True))

    return render(request, 'dashboard/branch.html', {'branch_summary': sorted_summary})



def degree(request):

    try:
        response = requests.get(registrations_url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return render(request, 'error.html', {'error': str(e)})

    # Initialize dictionaries to store counts by degree
    degree_summary = {degree: {'total': 0, 'verified': 0, 'non_verified': 0} for degree in DEGREES}

    # Process each record
    for record in data:
        degree = record.get('degree_name')
        verified = record.get('verified', False)

        # Update counts
        if degree in degree_summary:
            degree_summary[degree]['total'] += 1
            if verified:
                degree_summary[degree]['verified'] += 1
            else:
                degree_summary[degree]['non_verified'] += 1

    # Get sorting parameter from request
    sort_by = request.GET.get('sort_by', 'total')  # Default to sorting by total if no sort parameter is provided

    # Sort the result based on the selected sorting parameter
    if sort_by == 'verified':
        sorted_summary = dict(sorted(degree_summary.items(), key=lambda item: item[1]['verified'], reverse=True))
    elif sort_by == 'non_verified':
        sorted_summary = dict(sorted(degree_summary.items(), key=lambda item: item[1]['non_verified'], reverse=True))
    elif sort_by == 'degree':
        sorted_summary = dict(sorted(degree_summary.items()))  # Default sorting by Degree
    else:
        sorted_summary = dict(sorted(degree_summary.items(), key=lambda item: item[1]['total'], reverse=True))

    return render(request, 'dashboard/degree.html', {'degree_summary': sorted_summary})



def birth_place(request):

    try:
        response = requests.get(registrations_url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return render(request, 'error.html', {'error': str(e)})

    # Initialize dictionaries to store counts by birth place
    birth_state_summary = {state: {'total': 0, 'verified': 0, 'non_verified': 0} for state in INDIAN_STATES}

    # Process each record
    for record in data:
        birth_place = record.get('birth_place')
        verified = record.get('verified', False)

        # Update counts
        if birth_place in birth_state_summary:
            birth_state_summary[birth_place]['total'] += 1
            if verified:
                birth_state_summary[birth_place]['verified'] += 1
            else:
                birth_state_summary[birth_place]['non_verified'] += 1

    # Get sorting parameter from request
    sort_by = request.GET.get('sort_by', 'total')  # Default to sorting by total if no sort parameter is provided

    # Sort the result based on the selected sorting parameter
    if sort_by == 'verified':
        sorted_summary = dict(sorted(birth_state_summary.items(), key=lambda item: item[1]['verified'], reverse=True))
    elif sort_by == 'non_verified':
        sorted_summary = dict(sorted(birth_state_summary.items(), key=lambda item: item[1]['non_verified'], reverse=True))
    elif sort_by == 'state':
        sorted_summary = dict(sorted(birth_state_summary.items()))  # Default sorting by State
    else:
        sorted_summary = dict(sorted(birth_state_summary.items(), key=lambda item: item[1]['total'], reverse=True))

    return render(request, 'dashboard/birth-place.html', {'birth_state_summary': sorted_summary})



def passing_year(request):
    try:
        response = requests.get(registrations_url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return render(request, 'error.html', {'error': str(e)})

    # Initialize dictionaries to store counts
    yearly_summary = defaultdict(lambda: {'total': 0, 'verified': 0, 'non_verified': 0})

    # Process each record
    for record in data:
        passing_year = record.get('passing_year')
        verified = record.get('verified', False)

        # Validate and update counts
        if passing_year:
            try:
                year = int(passing_year)  # Ensure the passing_year is an integer
                yearly_summary[year]['total'] += 1
                if verified:
                    yearly_summary[year]['verified'] += 1
                else:
                    yearly_summary[year]['non_verified'] += 1
            except ValueError:
                # Skip records with invalid passing_year values
                continue

    # Prepare the result for a specific range of years
    result = {year: yearly_summary[year] for year in range(2010, 2030)}

    # Get the sorting parameter from the request
    sort_by = request.GET.get('sort_by', 'total')  # Default to sorting by total if no sort parameter is provided

    # Sort the result based on the selected sorting parameter
    if sort_by == 'verified':
        sorted_result = dict(sorted(result.items(), key=lambda item: item[1]['verified'], reverse=True))
    elif sort_by == 'non_verified':
        sorted_result = dict(sorted(result.items(), key=lambda item: item[1]['non_verified'], reverse=True))
    elif sort_by == 'year':
        sorted_result = dict(sorted(result.items()))  # Default sorting by year
    else:
        sorted_result = dict(sorted(result.items(), key=lambda item: item[1]['total'], reverse=True))

    return render(request, 'dashboard/passing-year.html', {'yearly_summary': sorted_result})

    

def college_state(request):
  
    try:
        response = requests.get(registrations_url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return render(request, 'error.html', {'error': str(e)})

    # Initialize dictionaries to store counts by state
    state_summary = defaultdict(lambda: {'total': 0, 'verified': 0, 'non_verified': 0})

    # Process each record
    for record in data:
        college_state = record.get('college_state')
        verified = record.get('verified', False)

        # Update counts
        if college_state:
            state_summary[college_state]['total'] += 1
            if verified:
                state_summary[college_state]['verified'] += 1
            else:
                state_summary[college_state]['non_verified'] += 1

    # Ensure all states are included in the result, even if they have no data
    for state in INDIAN_STATES:
        if state not in state_summary:
            state_summary[state] = {'total': 0, 'verified': 0, 'non_verified': 0}

    # Get sorting parameter from request
    sort_by = request.GET.get('sort_by', 'total')  # Default to sorting by total if no sort parameter is provided

    # Sort the result based on the selected sorting parameter
    if sort_by == 'verified':
        sorted_summary = dict(sorted(state_summary.items(), key=lambda item: item[1]['verified'], reverse=True))
    elif sort_by == 'non_verified':
        sorted_summary = dict(sorted(state_summary.items(), key=lambda item: item[1]['non_verified'], reverse=True))
    elif sort_by == 'state':
        sorted_summary = dict(sorted(state_summary.items()))  # Default sorting by State
    else:
        sorted_summary = dict(sorted(state_summary.items(), key=lambda item: item[1]['total'], reverse=True))

    return render(request, 'dashboard/college-state.html', {'state_summary': sorted_summary})

# ================================================================================== #





""" =========================================        D A S H B O A R D  &  S E C T I O N S   E N D         ======================================== """









""" ===================================================    S E P A R A T E   P A G E S   ========================================================= """


# =========================== C O M P L E T E D ==================================== #

def app_downloads(request):
    api_url = registrations_url
    sort_by = request.GET.get('sort_by', 'registered')  # Default to sorting by registered
    user_counts = count_verified_users_from_api(api_url, sort_by=sort_by)
    
    context = {
        'user_counts': user_counts,
        'sort_by': sort_by,  # Pass the sorting option to the template
        # Add any other context you need
    }
    
    return render(request, "app-download.html", context)

# ================================================================================== #


def verified(request):
    users_response = requests.get(registrations_url)
    verification_response = requests.get(verification_url)

    if users_response.status_code == 200:
        users_data = users_response.json()
    else:
        users_data = []

    if verification_response.status_code == 200:
        verification_data = verification_response.json()
        uid_map = {item["register"]: item["uid"] for item in verification_data}  # Map register ID to uid
    else:
        uid_map = {}

    # Get the search query and sort option from the request
    search_query = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    verified_data = []
    for user in users_data:
        if user.get('verified') == True:
            user_id = user.get("id")
            user["uid"] = uid_map.get(user_id, "--")  # Use user ID to get uid from uid_map

            time_end_str = user.get("time_end")

            if time_end_str:
                try:
                    # Convert string to datetime object in UTC
                    utc_datetime = datetime.strptime(time_end_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    # Localize datetime to UTC
                    utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)
                    # Convert UTC to IST
                    ist_timezone = pytz.timezone('Asia/Kolkata')
                    ist_datetime = utc_datetime.astimezone(ist_timezone)
                    # Extract the date part
                    user["time_end"] = ist_datetime.date()
                except ValueError as e:
                    # Handle any potential errors in parsing the datetime
                    user["time_end"] = f"Error parsing date: {e}"
            else:
                user["time_end"] = "--"

            # Add the user to the verified_data list if the search query matches
            if search_query:
                search_query_lower = search_query.lower()
                if (
                    search_query_lower in user.get("full_name", "").lower().strip() or
                    search_query_lower in user.get("email", "").lower().strip() or
                    search_query_lower in user.get("uid", "").lower().strip() or
                    search_query_lower in user.get("phone_number", "").lower().strip() or
                    search_query_lower in user.get("branch_name", "").lower().strip() or
                    search_query_lower in user.get("degree_name", "").lower().strip() or
                    search_query_lower in str(user.get("passing_year", "")).lower().strip() or
                    search_query_lower in user.get("college_name", "").lower().strip()
                ):
                    verified_data.append(user)
            else:
                verified_data.append(user)

    # Sorting logic applied to verified_data
    if sort_by:
        if sort_by == "full_name":
            verified_data = sorted(verified_data, key=lambda x: x.get("full_name", "").lower())
        elif sort_by == "passing_year":
            verified_data = sorted(verified_data, key=itemgetter("passing_year"))
        elif sort_by == "verified":
            verified_data = sorted(verified_data, key=itemgetter("verified"), reverse=True)

    # Check if no data was found
    no_data_found = len(verified_data) == 0

    # Pagination
    paginator = Paginator(verified_data, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "verified.html", {
        "page_obj": page_obj,
        "search_query": search_query,
        "no_data_found": no_data_found
    })



def not_verified(request):
    users_response = requests.get(registrations_url)
    verification_response = requests.get(verification_url)

    if users_response.status_code == 200:
        users_data = users_response.json()
    else:
        users_data = []

    if verification_response.status_code == 200:
        verification_data = verification_response.json()
        uid_map = {item["id"]: item["uid"] for item in verification_data}
    else:
        uid_map = {}

    # Get the search query and sort option from the request
    search_query = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    not_verified_data = []
    for user in users_data:
        if user.get('verified') == False:
            user_id = user.get("id")
            user["uid"] = uid_map.get(user_id, "--")

            time_end_str = user.get("time_end")
            if time_end_str:
                try:
                    # Convert string to datetime object in UTC
                    utc_datetime = datetime.strptime(time_end_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    # Localize datetime to UTC
                    utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)
                    # Convert UTC to IST
                    ist_timezone = pytz.timezone('Asia/Kolkata')
                    ist_datetime = utc_datetime.astimezone(ist_timezone)
                    # Extract the date part
                    user["time_end"] = ist_datetime.date()
                    print(user['time_end'])
                except ValueError as e:
                    # Handle any potential errors in parsing the datetime
                    user["time_end"] = f"Error parsing date: {e}"
            else:
                user["time_end"] = "--"

            # Add the user to the not_verified_data list if the search query matches
            if search_query:
                search_query_lower = search_query.lower()
                if (
                    search_query_lower in user.get("full_name", "").lower().strip() or
                    search_query_lower in user.get("email", "").lower().strip() or
                    search_query_lower in user.get("uid", "").lower().strip() or
                    search_query_lower in user.get("phone_number", "").lower().strip() or
                    search_query_lower in user.get("branch_name", "").lower().strip() or
                    search_query_lower in user.get("degree_name", "").lower().strip() or
                    search_query_lower in str(user.get("passing_year", "")).lower().strip() or
                    search_query_lower in user.get("college_name", "").lower().strip()
                ):
                    not_verified_data.append(user)
            else:
                not_verified_data.append(user)

    # Sorting logic applied to not_verified_data
    if sort_by:
        if sort_by == "full_name":
            not_verified_data = sorted(not_verified_data, key=lambda x: x.get("full_name", "").lower())
        elif sort_by == "passing_year":
            not_verified_data = sorted(not_verified_data, key=itemgetter("passing_year"))
        elif sort_by == "verified":
            not_verified_data = sorted(not_verified_data, key=itemgetter("verified"), reverse=True)

    # Check if no data was found
    no_data_found = len(not_verified_data) == 0

    # Pagination
    paginator = Paginator(not_verified_data, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "not-verified.html", {
        "page_obj": page_obj,
        "search_query": search_query,
        "no_data_found": no_data_found
    })



def total_user(request):
    users_response = requests.get(registrations_url)
    verification_response = requests.get(verification_url)

    if users_response.status_code == 200:
        users_data = users_response.json()
    else:
        users_data = []

    if verification_response.status_code == 200:
        verification_data = verification_response.json()
        uid_map = {item["register"]: item["uid"] for item in verification_data}
    else:
        uid_map = {}

    for user in users_data:
        user_id = user.get("id")
        user["uid"] = uid_map.get(user_id, "--")

        # Extract the date part from the 'time_end' field
        time_end_str = user.get("time_end")
        if time_end_str:
            try:
                # Convert string to datetime object in UTC
                utc_datetime = datetime.strptime(time_end_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                # Localize datetime to UTC
                utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)
                # Convert UTC to IST
                ist_timezone = pytz.timezone('Asia/Kolkata')
                ist_datetime = utc_datetime.astimezone(ist_timezone)
                # Extract the date part
                user["time_end"] = ist_datetime.date()
                print(user['time_end'])
            except ValueError as e:
                # Handle any potential errors in parsing the datetime
                user["time_end"] = f"Error parsing date: {e}"
        else:
            user["time_end"] = "--"

    # Get the search query from the request, trimming whitespace
    search_query = request.GET.get("search", "").strip()

    if search_query:
        search_query = search_query.lower()
        users_data = [
            user for user in users_data if (
                search_query in user.get("full_name", "").lower().strip() or
                search_query in user.get("email", "").lower().strip() or
                search_query in user.get("uid", "").lower().strip() or
                search_query in user.get("phone_number", "").lower().strip() or
                search_query in user.get("branch_name", "").lower().strip() or
                search_query in user.get("degree_name", "").lower().strip() or
                search_query in str(user.get("passing_year", "")).lower().strip() or
                search_query in user.get("college_name", "").lower().strip()
            )
        ]

    # Sorting
    sort_by = request.GET.get("sort_by", "").strip()

    if sort_by:
        if sort_by == "full_name":
            users_data = sorted(users_data, key=lambda x: x.get("full_name", "").lower())
        elif sort_by == "not_verified":
            users_data = sorted(users_data, key=itemgetter("verified"),reverse=False)
        elif sort_by == "college_name":
            users_data = sorted(users_data, key=itemgetter("college_name"))
        elif sort_by == "passing_year":
            users_data = sorted(users_data, key=itemgetter("passing_year"))
        elif sort_by == "verified":
            users_data = sorted(users_data, key=itemgetter("verified"), reverse=True)

    # Check if no data found
    no_data_found = len(users_data) == 0

    items_per_page = 10
    paginator = Paginator(users_data, items_per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "total-user.html", {"page_obj": page_obj, "search_query": search_query, "no_data_found": no_data_found})







def internship(request):
    # Fetch data once
    data = requests.get(internship_application_url).json()

    # Count total number of internships
    intern_count = len(data)
    
    selected_count = 0
    # Filter and count selected and rejected internships
    selected_data = [internship for internship in data if internship.get('candidate_status') == 'Select']
    rejected_data = [internship for internship in data if internship.get('candidate_status') == 'Reject']

    
    selected_count = len(selected_data)
    print(selected_count)
    rejected_count = len(rejected_data)


#  This code is used to show the selected candidate data in template
#    --------------------------------------------------------------------------
    applications_url = "http://13.127.246.196:8000/api/internship-applications/"
    registers_url = "http://13.127.246.196:8000/api/registers/"

    # Fetch data from the internship applications API
    applications_response = requests.get(applications_url)
    if applications_response.status_code == 200:
        applications_data = applications_response.json()
            # Extract specific fields where candidate_status is "Select"
        extracted_applications_data = [
        {
            "candidate_status": item.get("candidate_status"),
            "current_year": item.get("current_year"),
            "internship": item.get("internship"),
            "register": item.get("register")
        }
        for item in applications_data if item.get("candidate_status") == "Select"
         ]
    else:
     extracted_applications_data = []

    # Fetch data from the registers API
    registers_response = requests.get(registers_url)
    if registers_response.status_code == 200:
        registers_data = registers_response.json()
    else:
        registers_data = []

    # Create a dictionary to map user_id to their register data
    registers_map = {register["id"]: register for register in registers_data}

# Combine data for users who have applied for internships and have candidate_status as "Select"
    selected_data = []
    for application in extracted_applications_data:
        user_id = application.get("register")
        if user_id in registers_map:
            combined_item = application.copy()
            combined_item.update(registers_map[user_id])
            selected_data.append(combined_item)

        print(selected_data, "Filtered Data")
    # ---------------------------------------------------------


    # this code is used for showing rejected candidates data to template
    # -------------------------------------------------------------------
    applications_url = "http://13.127.246.196:8000/api/internship-applications/"
    registers_url = "http://13.127.246.196:8000/api/registers/"

    # Fetch data from the internship applications API
    applications_response = requests.get(applications_url)
    if applications_response.status_code == 200:
        applications_data = applications_response.json()
            # Extract specific fields where candidate_status is "Select"
        extracted_applications_data = [
        {
            "candidate_status": item.get("candidate_status"),
            "current_year": item.get("current_year"),
            "internship": item.get("internship"),
            "register": item.get("register")
        }
        for item in applications_data if item.get("candidate_status") == "Reject"
         ]
    else:
     extracted_applications_data = []

    # Fetch data from the registers API
    registers_response = requests.get(registers_url)
    if registers_response.status_code == 200:
        registers_data = registers_response.json()
    else:
        registers_data = []

    # Create a dictionary to map user_id to their register data
    registers_map = {register["id"]: register for register in registers_data}

# Combine data for users who have applied for internships and have candidate_status as "Select"
    rejected_data = []
    for application in extracted_applications_data:
        user_id = application.get("register")
        if user_id in registers_map:
            combined_item = application.copy()
            combined_item.update(registers_map[user_id])
            rejected_data.append(combined_item)

        print(rejected_data, "Filtered Data")


# this code is used to show internship-applied candidate data in template
# -------------------------------------------------------------------------------
    applications_url = "http://13.127.246.196:8000/api/internship-applications/"
    registers_url = "http://13.127.246.196:8000/api/registers/"


    # Fetch data from the internship applications API
    applications_response = requests.get(applications_url)
    if applications_response.status_code == 200:
        applications_data = applications_response.json()
        # Extract specific fields: candidate_status, current_year, internship
        extracted_applications_data = [
            {
                "candidate_status": item.get("candidate_status"),
                "current_year": item.get("current_year"),
                "internship": item.get("internship"),
                "register": item.get("register")  # Assuming there's a user_id field to match with registers
            }
            for item in applications_data
        ]
    else:
        extracted_applications_data = []

    # Fetch data from the registers API
    registers_response = requests.get(registers_url)
    if registers_response.status_code == 200:
        registers_data = registers_response.json()
    else:
        registers_data = []

    # Create a dictionary to map user_id to their register data
    registers_map = {register["id"]: register for register in registers_data}

    # Combine data for users who have applied for internships
    combined_data = []
    for application in extracted_applications_data:
        user_id = application.get("register")
        if user_id in registers_map:
            combined_item = application.copy()
            combined_item.update(registers_map[user_id])
            combined_data.append(combined_item)

    print(selected_data,"hii")
    context = {
        'intern_count': intern_count,
        'data1': data,
        'selected_count': selected_count,
        'rejected_count': rejected_count,
        # this is for table data
        'selected_data': selected_data,
        'rejected_data': rejected_data,
        "combined_data": combined_data
    }

    return render(request, "internship.html", context)



def fresher_Job(request):
    fresher_data = requests.get(fresher_Job_url).json()
    fresher_count = len(fresher_data)
    selected_count = 0
    selected_data = [fresher for fresher in fresher_data if fresher.get('candidate_status') == 'Select']
    rejected_data = [fresher for fresher in fresher_data if fresher.get('candidate_status') == 'Reject']

    selected_count = len(selected_data)
    print(selected_count)
    rejected_count = len(rejected_data)


# -----------------------------------------------------------------------
    applications_url = "http://13.127.246.196:8000/api/job-applications/"
    registers_url = "http://13.127.246.196:8000/api/registers/"

    # Fetch data from the internship applications API
    applications_response = requests.get(applications_url)
    if applications_response.status_code == 200:
        applications_data = applications_response.json()
            # Extract specific fields where candidate_status is "Select"
        extracted_applications_data = [
        {
            "candidate_status": item.get("candidate_status"),
            "current_year": item.get("current_year"),
            "internship": item.get("internship"),
            "register": item.get("register")
        }
        for item in applications_data if item.get("candidate_status") == "Select"
         ]
    else:
     extracted_applications_data = []

    # Fetch data from the registers API
    registers_response = requests.get(registers_url)
    if registers_response.status_code == 200:
        registers_data = registers_response.json()
    else:
        registers_data = []

    # Create a dictionary to map user_id to their register data
    registers_map = {register["id"]: register for register in registers_data}

# Combine data for users who have applied for internships and have candidate_status as "Select"
    selected_data = []
    for application in extracted_applications_data:
        user_id = application.get("register")
        if user_id in registers_map:
            combined_item = application.copy()
            combined_item.update(registers_map[user_id])
            selected_data.append(combined_item)

        print(selected_data, "Filtered Data")

# -----------------------------------------------------------------------------
    applications_url = "http://13.127.246.196:8000/api/job-applications/"
    registers_url = "http://13.127.246.196:8000/api/registers/"

    # Fetch data from the internship applications API
    applications_response = requests.get(applications_url)
    if applications_response.status_code == 200:
        applications_data = applications_response.json()
            # Extract specific fields where candidate_status is "Select"
        extracted_applications_data = [
        {
            "candidate_status": item.get("candidate_status"),
            "current_year": item.get("current_year"),
            "internship": item.get("internship"),
            "register": item.get("register")
        }
        for item in applications_data if item.get("candidate_status") == "Reject"
         ]
    else:
     extracted_applications_data = []

    # Fetch data from the registers API
    registers_response = requests.get(registers_url)
    if registers_response.status_code == 200:
        registers_data = registers_response.json()
    else:
        registers_data = []

    # Create a dictionary to map user_id to their register data
    registers_map = {register["id"]: register for register in registers_data}

# Combine data for users who have applied for internships and have candidate_status as "Select"
    rejected_data = []
    for application in extracted_applications_data:
        user_id = application.get("register")
        if user_id in registers_map:
            combined_item = application.copy()
            combined_item.update(registers_map[user_id])
            rejected_data.append(combined_item)

        print(rejected_data, "Filtered Data")



# -----------------------------------------------------------------

    applications_url = "http://13.127.246.196:8000/api/job-applications/"
    registers_url = "http://13.127.246.196:8000/api/registers/"

    # Fetch data from the internship applications API
    applications_response = requests.get(applications_url)
    if applications_response.status_code == 200:
        applications_data = applications_response.json()
        # Extract specific fields: candidate_status, current_year, internship
        extracted_applications_data = [
            {
                "candidate_status": item.get("candidate_status"),
                "current_year": item.get("current_year"),
                "fresherjob": item.get("fresherjob"),
                "register": item.get("register")  # Assuming there's a user_id field to match with registers
            }
            for item in applications_data
        ]
    else:
        extracted_applications_data = []

    # Fetch data from the registers API
    registers_response = requests.get(registers_url)
    if registers_response.status_code == 200:
        registers_data = registers_response.json()
    else:
        registers_data = []

    # Create a dictionary to map user_id to their register data
    registers_map = {register["id"]: register for register in registers_data}

    # Combine data for users who have applied for internships
    combined_data = []
    for application in extracted_applications_data:
        user_id = application.get("register")
        if user_id in registers_map:
            combined_item = application.copy()
            combined_item.update(registers_map[user_id])
            combined_data.append(combined_item)

    context={
      'fresher_count':fresher_count ,
      "combined_data": combined_data ,
      "selected_data":selected_data,
      "rejected_data":rejected_data,
      "rejected_count":rejected_count,
      "selected_count":selected_count
    }
     
    return render(request,"fresher-job.html",context)




def experienced(request):
    experience_data = requests.get(experience_Job_url).json()
    experience_count = len(experience_data)

    selected_data = [experience for experience in experience_data if experience.get('candidate_status') == 'Select']
    rejected_data = [experience for experience in experience_data if experience.get('candidate_status') == 'Reject']

    selected_count = len(selected_data)
    print(selected_count)
    rejected_count = len(rejected_data)


    # This code is used use to selected candidate to template
    # -----------------------------------------------------------------------
    applications_url = "http://13.127.246.196:8000/api/experience-job-applications/"
    registers_url = "http://13.127.246.196:8000/api/registers/"

    # Fetch data from the internship applications API
    applications_response = requests.get(applications_url)
    if applications_response.status_code == 200:
        applications_data = applications_response.json()
            # Extract specific fields where candidate_status is "Select"
        extracted_applications_data = [
        {
            "candidate_status": item.get("candidate_status"),
            "current_year": item.get("current_year"),
            "internship": item.get("internship"),
            "register": item.get("register")
        }
        for item in applications_data if item.get("candidate_status") == "Select"
         ]
    else:
     extracted_applications_data = []

    # Fetch data from the registers API
    registers_response = requests.get(registers_url)
    if registers_response.status_code == 200:
        registers_data = registers_response.json()
    else:
        registers_data = []

    # Create a dictionary to map user_id to their register data
    registers_map = {register["id"]: register for register in registers_data}

# Combine data for users who have applied for internships and have candidate_status as "Select"
    selected_data = []
    for application in extracted_applications_data:
        user_id = application.get("register")
        if user_id in registers_map:
            combined_item = application.copy()
            combined_item.update(registers_map[user_id])
            selected_data.append(combined_item)

        print(selected_data, "Filtered Data")



# this code is used to show to rejected candidate on the template
# -----------------------------------------------------------------------------
    applications_url = "http://13.127.246.196:8000/api/experience-job-applications/"
    registers_url = "http://13.127.246.196:8000/api/registers/"

    # Fetch data from the internship applications API
    applications_response = requests.get(applications_url)
    if applications_response.status_code == 200:
        applications_data = applications_response.json()
            # Extract specific fields where candidate_status is "Select"
        extracted_applications_data = [
        {
            "candidate_status": item.get("candidate_status"),
            "current_year": item.get("current_year"),
            "internship": item.get("internship"),
            "register": item.get("register")
        }
        for item in applications_data if item.get("candidate_status") == "Reject"
         ]
    else:
     extracted_applications_data = []

    # Fetch data from the registers API
    registers_response = requests.get(registers_url)
    if registers_response.status_code == 200:
        registers_data = registers_response.json()
    else:
        registers_data = []

    # Create a dictionary to map user_id to their register data
    registers_map = {register["id"]: register for register in registers_data}

# Combine data for users who have applied for internships and have candidate_status as "Select"
    rejected_data = []
    for application in extracted_applications_data:
        user_id = application.get("register")
        if user_id in registers_map:
            combined_item = application.copy()
            combined_item.update(registers_map[user_id])
            rejected_data.append(combined_item)

        print(rejected_data, "Filtered Data")



# This code is used to show experience joj on template 
# ---------------------------------------------------------------------------

    applications_url = "http://13.127.246.196:8000/api/experience-job-applications/"
    registers_url = "http://13.127.246.196:8000/api/registers/"

    # Fetch data from the internship applications API
    applications_response = requests.get(applications_url)
    if applications_response.status_code == 200:
        applications_data = applications_response.json()
        # Extract specific fields: candidate_status, current_year, internship
        extracted_applications_data = [
            {
                "candidate_status": item.get("candidate_status"),
                "current_year": item.get("current_year"),
                "fresherjob": item.get("fresherjob"),
                "register": item.get("register")  # Assuming there's a user_id field to match with registers
            }
            for item in applications_data
        ]
    else:
        extracted_applications_data = []

    # Fetch data from the registers API
    registers_response = requests.get(registers_url)
    if registers_response.status_code == 200:
        registers_data = registers_response.json()
    else:
        registers_data = []

    # Create a dictionary to map user_id to their register data
    registers_map = {register["id"]: register for register in registers_data}

    # Combine data for users who have applied for internships
    combined_data = []
    for application in extracted_applications_data:
        user_id = application.get("register")
        if user_id in registers_map:
            combined_item = application.copy()
            combined_item.update(registers_map[user_id])
            combined_data.append(combined_item)


    context={
      'experience_count':experience_count ,
      "selected_count":selected_count,
      "rejected_count":rejected_count,
      "combined_data":combined_data,
      "selected_data":selected_data,
      "rejected_data":rejected_data,

    }
    return render(request,"experienced.html",context)




def corporate_training(request):
    corporate_count = requests.get(corporate_training_url).json()
    corporate_count = len(corporate_count)
    context={
      'corporate_count':corporate_count ,
      
    }
    return render(request,"corporate-training.html",context)


def mentorship(request):
    return render(request,"mentorship.html")


def Query(request):
    # response = requests.get(queries_url)
    # data = response.json()
    
    # query_count = len(data)
    # open_query_count = 0
    # closed_query_count = 0

    # for query in data:
    #     if query.get('status') == 'open':
    #         open_query_count += 1
    #     elif query.get('status') == 'closed':
    #         closed_query_count += 1
            
    # register = query.get('register')
    # if register:
    #     user_response = requests.get(f'http://13.127.246.196:8000/api/registers/')
    #     user_data = user_response.json()
    #     query['register'] = user_data.get('full_name')  # Replace register number with user name
        

    # context = {
    #     'data': data,
    #     'query_count': query_count,
    #     'open_query_count': open_query_count,
    #     'closed_query_count': closed_query_count,
    # }
    return render(request, 'Query.html')    



def Query_view(request,pk):
     # API endpoint
    url = f'http://13.127.246.196:8000/api/queries/{pk}/'
    
    try:
        # Make the GET request to the API
        response = requests.get(url)
        response.raise_for_status()  # Raises error for bad responses
        query_data = response.json()  # Parse the JSON response

        # Pass the data to the template
        return render(request ,'Query-view.html',{'query_data': query_data})

    except requests.exceptions.HTTPError as err:
        # Handle the error, return a custom error message
        return HttpResponse(f"Error: {err}", status=400)




def internship_from(request):
    return render(request,'internship-form.html')   

def create_internship_job(request):
    if request.method == 'POST':
        # Collect form data based on the fields from your template
        internship_data = {
            'company_name': request.POST.get('company-name'),
            'about_company': request.POST.get('about_company'),
            'internship_profile': request.POST.get('intern-profile'),
            'job_description': request.POST.get('job_description'),
            'education_required': request.POST.get('education_required'),
            'internship_type': request.POST.get('internship-type'),  # Radio buttons for 'In Office', 'Hybrid', 'Remote'
            'location': request.POST.get('location'),
            'duration': request.POST.get('duration'),
            'benefits': request.POST.get('benefits'),
            'stipend_type': request.POST.get('stipend-type'),  # Radio buttons for 'Fixed', 'Negotiable', 'Unpaid'
            'amount': request.POST.get('amount'),  # The stipend amount
            'perks': request.POST.getlist('perks'),  # Collect multiple perks (checklist)
            'responsibilities': request.POST.get('responsibilities'),
            'alt_mobile': request.POST.get('alt_mobile'),  # Alternate mobile number for the listing
            'skills_required': request.POST.get('skills_required'),  # Skills required
        }

        # Convert perks to a string if it's a list
        if isinstance(internship_data['perks'], list):
            internship_data['perks'] = ', '.join(internship_data['perks'])

        # API endpoint for posting the internship
        api_url = 'http://13.127.246.196:8000/api/internship/'  # Replace with your API endpoint

        try:
            # Make the POST request to the API with internship data as JSON
            response = requests.post(api_url, json=internship_data, headers={'Content-Type': 'application/json'})
            response.raise_for_status()  # Raises an error for bad responses

            # Redirect to a success page if the API call is successful
            return redirect('success_page')  # Replace 'success_page' with your actual success URL

        except requests.exceptions.HTTPError as err:
            # Handle any errors that occur during the POST request
            error_message = response.text  # or response.json() if the response is in JSON format
            return HttpResponse(f"Error: {err}. Details: {error_message}", status=400)

    # Render the internship form if it's a GET request
    return render(request, 'internship_form.html')


def fresher_from(request):
    return render(request,'fresher-form.html')  

def create_fresher_job(request):
    if request.method == 'POST':
        # Collect form data
        fresher_job_data = {
            'Job profile': request.POST.get('fresher-profile'),
            'Job type': request.POST.get('internship-type'),
            'Location': request.POST.get('location'),
            'Min experience': request.POST.get('min_experience'),
            'Max experience': request.POST.get('max_experience'),
            'Min CTC': request.POST.get('min_ctc'),
            'Max CTC': request.POST.get('max_ctc'),
            'Perks': request.POST.getlist('perks'),  # Collect perks as a list
            'Alt mobile': request.POST.get('alt_mobile'),
            'Skills required': request.POST.get('skills_required'),
            # Add other fields if necessary
        }

        # API endpoint
        url = 'http://13.127.246.196:8000/api/jobs/'  # Replace with your API endpoint

        try:
            # Make the POST request to the API
            response = requests.post(url, data=fresher_job_data)
            response.raise_for_status()  # Raises an error for bad responses

            # Redirect or show success message
            return redirect('success')  # Assuming you have a 'success' page

        except requests.exceptions.HTTPError as err:
            # Handle the error, return a custom error message
            return HttpResponse(f"Error: {err}", status=400)

    return render(request,'fresher-form.html')    


def experienced_from(request):
    return render(request,'experienced-form.html')        
