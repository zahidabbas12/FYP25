from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip session check for login and logout pages
        if request.path in [reverse('login'), reverse('logout')]:
            return self.get_response(request)

        # Check if user is authenticated
        if request.user.is_authenticated:
            # Get last activity from session
            last_activity_str = request.session.get('last_activity')
            
            if last_activity_str:
                try:
                    # Convert string back to datetime
                    last_activity = datetime.fromisoformat(last_activity_str)
                    
                    # Calculate time since last activity
                    time_since_last_activity = timezone.now() - last_activity
                    
                    # If more than 1 hour has passed, log the user out
                    if time_since_last_activity > timedelta(hours=1):
                        # Clear the session
                        request.session.flush()
                        # Add message for the user
                        messages.warning(request, 'Your session has expired due to inactivity. Please log in again.')
                        # Redirect to login page
                        return redirect('login')
                except (ValueError, TypeError):
                    # If there's any error with the datetime conversion, just update the activity time
                    pass
            
            # Update last activity time as ISO format string
            request.session['last_activity'] = timezone.now().isoformat()

        return self.get_response(request) 