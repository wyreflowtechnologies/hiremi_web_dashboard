import pytz
from django.utils import timezone

def last_login_processor(request):
    last_login = None

    if request.user.is_authenticated:
        last_login = request.user.last_login
        if last_login:
            # Ensure last_login is treated as UTC if naive
            if timezone.is_naive(last_login):
                last_login = timezone.make_aware(last_login, timezone.utc)
            
            # Convert to IST
            ist_timezone = pytz.timezone('Asia/Kolkata')
            last_login = last_login.astimezone(ist_timezone)
            
            # Format the date and time in IST with GMT offset
            last_login = last_login.strftime('%A, %d %B, %Y %H:%M:%S') + ' GMT+5:30'
    
    return {'last_login': last_login}
