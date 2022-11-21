from django.shortcuts import render
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from rest_framework.decorators import api_view
from .helpers import send_otp_to_phone

# Create your views here.
@login_required(login_url='login_view')
def index(request):
    return render(request, 'rishabs/shop.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if User.objects.get(phone_number=username).is_phone_verified:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, 'rishabs/login.html', {'message': 'Invalid Credentials'})

    return render(request, 'rishabs/login.html')



def register_view(request):

    if request.method == "POST":
        name = request.POST["username"]
        password = request.POST["password"]
        password2 = request.POST["cpassword"]
        phone_number = request.POST["phone_number"]

        if password == password2 and password!=None:

            user = User.objects.create_user(
                username = name,
                password = password,
                phone_number = phone_number,
                otp = send_otp_to_phone(phone_number)
            )
            user.set_password = password
            user.save()

            return render(request, 'rishabs/verify.html')

        else:
            return render(request, 'rishabs/register.html', {'message': 'Passwords do not match'})


    return render(request, 'rishabs/register.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login_view"))

@api_view(['POST'])
def verify(request):
    if request.method == "POST":
        phone_number = request.POST["phone_number"]
        otp1 = request.POST["otp1"]

        try:
            user_obj = User.objects.get(phone_number = phone_number)

        except Exception as e:
            return render(request, 'rishabs/verify.html', {'message': 'Phone Number does not Exists'})
    
        if user_obj.otp == otp1:
            user_obj.is_phone_verified = True
            user_obj.save()
            return render(request, 'rishabs/shop.html')

        return render(request, 'rishabs/verify.html', {'message': 'Phone Number does not Exists'})

    else:
        return render(request, 'rishabs/verify.html')