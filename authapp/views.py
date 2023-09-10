from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from .utils import TokenGenerator, generate_token
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError
from django.contrib.auth import authenticate,login,logout
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your views here.


         
def signup(request):
    if request.method == 'POST':
        email=request.POST['email']
        password=request.POST['pass1']
        confirm_password=request.POST['pass2']
        if password != confirm_password:

            messages.warning(request,"Password do not Match,Please Try Again!")
            return render(request,'signup.html')
        try:
            if User.objects.get(username=email):
                # return HttpResponse('alreday exist')
                messages.warning(request,"Email Already Exists")
                return redirect('/signup')
        except Exception as identifier:            
            pass 
        
        user=User.objects.create_user(email,email,password)
        user.save()
        # messages.info(request,'Thanks For Signing Up')
        messages.info(request,"Signup Successful Please Login")
        # return HttpResponse("user created",email)
        return redirect('/auth/login')    
    return render(request,"signup.html") 

          
def handlelogin(request):
      if request.method == 'POST':
        # get parameters
        loginusername=request.POST['email']
        loginpassword=request.POST['pass1']
        user=authenticate(username=loginusername,password=loginpassword)
       
        if user is not None:
            login(request,user)
            # messages.info(request,"Successfully Logged In")
            return redirect('/')

        else:
            messages.error(request,"Invalid Credentials")
            return redirect('/login')    

         

      return render(request,'login.html')     


# def handlelogin(request):
#     return render (request,"login.html")

def handlelogout(request):
    logout(request)
    messages.warning(request,"Logout Success")
    return redirect('/auth/login')

