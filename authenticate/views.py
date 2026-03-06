from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . models import PasswordReset
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone

# Create your views here.

def signup(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_data_has_error = False
        
        if User.objects.filter( username = username ).exists():
            user_data_has_error = True
            messages.error(request, 'This username already exists')
            
        if User.objects.filter( email = email ).exists():
            user_data_has_error = True
            messages.error(request, 'This email is already taken.')
        
        if len( password ) < 5:
            user_data_has_error = True
            messages.error(request, 'The length of the password must be of minimum of five characters.')
        
        if user_data_has_error == True:
            return redirect('signup')
        else:
            user = User.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                username = username,
                email = email,
                password = password,
            )
            user.save()
            messages.success(request, 'This user is successfully created.')
            return redirect('signup')
    return render(request, 'authenticate/signup.html')


def LoginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password = password )
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'There is error in the credentials')
    return render(request, 'authenticate/login.html')


def LogoutView(request):
    logout(request)
    return redirect('home')


def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get( email = email )
            new_password_reset = PasswordReset( user = user )
            new_password_reset.save()
            
            password_reset_url = reverse('reset_password', kwargs = {'reset_id': new_password_reset.reset_id})
            full_password_reset_url = f"{ request.scheme}://{request.get_host()}{ password_reset_url }"
            
            email_body = f"Reset your password from below link:\n\n\n{ full_password_reset_url }"
            email_message = EmailMessage(
                'Password Reset Link',
                email_body,
                settings.EMAIL_HOST_USER,
                [ email ]
            )
            email_message.fail_silently = True
            email_message.send()
            
            messages.success(request, 'The reset link has been sent.')
            return redirect ('forget_password_sent', reset_id = new_password_reset.reset_id)
        except User.DoesNotExist:
            messages.error(request, f'This user does not exists with this { email }.')
    return render(request, 'authenticate/forget_password.html')


def forget_password_sent(request, reset_id):
    if PasswordReset.objects.filter(reset_id = reset_id).exists():
        return render(request, 'authenticate/forget_password_sent.html')
    else:
        messages.error(request, 'This reset id does not exists')
        return redirect('forget_password')


def reset_password(request, reset_id):
    try:
        password_reset_id = PasswordReset.objects.get( reset_id = reset_id )
            
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            password_have_error = False
            
            if len( password ) < 5:
                messages.error ( request, 'The length of password must be minimum of Five characters long.')
                password_have_error = True
            
            if password != confirm_password:
                password_have_error = True
                messages.error(request, 'The Password does not match with Confirm Password')
            
            expiration_time = password_reset_id.created_at + timezone.timedelta( minutes = 10 )
            if timezone.now() > expiration_time:
                password_have_error = True
                messages.error(request, 'The link has expired')
            
            if password_have_error == True:
                return redirect('reset_password', reset_id = password_reset_id.reset_id)
            
            if not password_have_error:
                user = password_reset_id.user
                user.set_password( password )
                user.save()
                
                password_reset_id.delete()
                messages.success(request, 'The Password Reset Has been successful.')
            
            else:
                return redirect('reset_password', reset_id = reset_id)
            
    except PasswordReset.DoesNotExist:
        messages.error(request, 'Password Reset does not exists.')
        return redirect('forget_password')
    return render(request, 'authenticate/reset_password.html')