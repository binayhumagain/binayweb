# from multiprocessing import context
# from pydoc_data.topics import 
from base64 import urlsafe_b64decode, urlsafe_b64encode
from email import message
from studybud import settings
from multiprocessing import context
from pickle import FALSE
from pydoc_data.topics import topics
from unicodedata import name
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required # For restring certain pages from unauthenticated Users
from django.db.models import Q #for Search function, OR   AND etc
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
# from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse

from base.forms import RoomForm, UserForm, MyUserCreationForm
from .models import Message, Room, Topic, User

from django.contrib import messages
from studybud import settings
from .tokens import generate_tokens
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage, send_mail

# rooms=[   
#     {'id': 1, 'name':'Lets learn Python'},
#     {'id': 2, 'name':'Design with me'},
#     {'id': 3, 'name':'Frontend Developers'},    
# ]
# def loginpage(request):
#     context = {}
#     return render (request, 'base.html/login_register', context)
def loginPage(request):
    page ='login'                           #Two links for same template login_register
    if request.user.is_authenticated:       
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try: 
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')    

        user = authenticate (request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password Invalid') 

    context={'page':page}
    return render (request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):   #Two links for same template
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm (request.POST)
        if form.is_valid():
            user=form.save(commit=False)            #Get User details immediately
            user.username = user.username.lower()
            user.is_active = False
            user.save()
            # login(request, user)
            
            subject = 'Welcome to email by Binay'
            message = 'Hello!' +user.username+ 'Welcome to Studybud! \n Thankyou for visiting! \n Please confirm your email address to proceed'
            from_email = settings.EMAIL_HOST_USER
            to_list = [user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)

        
            #Confirmation Email
            current_site = get_current_site(request)
            email_subject = 'Confirm your email to Studybud'
            message2 = render_to_string('email_confirmation.html', {
            'name' : user.first_name,
            'domain' : current_site.domain,
            'uid' : urlsafe_b64encode(force_bytes(user.pk)).decode(),
            'token' : generate_tokens.make_token(user)
            })

            email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [user.email],
            )
            email.fail_silently = True
            email.send()
            messages.success(request,'Your account has been created, Plese check email and activate')
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    return render(request, 'base/login_register.html', {'form':form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''    #Q lookup for Search
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 
        )   #for search, icontains=atleast contains
    topics = Topic.objects.all()[0:5]    #Limit only 5 topics in the sidebar
    room_count = rooms.count()  #default count query
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))    #For Recent Activity in Specific Rooms

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages= room.message_set.all() #room.modelname_set.all()   to get message of specific room
    participants = room.participants.all()        #one to one ma _set.all jastai many to many ma  

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')   #Get the message typed by user
        )
        room.participants.add(request.user)   #this user will be added as participants        other fns remove etc are available
        return redirect('room', pk=room.id)
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}        #for room template
    return render(request, 'base/room.html', context)
# Create your views here.

def userProfile (request, pk):
    user= User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()                                           #add to userprofile Page
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url= 'login')
def createroom(request):
    form = RoomForm()
    topics = Topic.objects.all()  #For passing to template datalist form
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description = request.POST.get('description'),
        )
        # if form.is_valid():
        #     room = form.save(commit=FALSE)
        #     room.host = request.user                    #2 lines done later for auto post host by logged in user
        #     room.save()         
        return redirect('home')   #because name=home in views
    context = {'form' : form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url= 'login')
def updateroom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) #because all data should be same
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not Allowed to Make changes')
    if request.method=='POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        room.save()
        return redirect('home')
    context = {'form' : form, 'topics':topics, 'room': room}
    return render (request, 'base/room_form.html', context)

@login_required(login_url= 'login')
def deleteRoom(request, pk):
    
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not Allowed to Make changes')    #When user is not the host
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url= 'login')
def deleteMessage(request, pk):
    
    message = Message.objects.get(id=pk)            #Get all fields of Message Class from Model

    if request.user != message.user:
        return HttpResponse('You are not Allowed to Make changes')    #When user is not the host
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form':form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)   #For Browse Topic Option
    return render(request, 'base/topics.html', {'topics':topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages':room_messages})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_b64decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    
    if myuser is not None and generate_tokens.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')

def error_404_view(request, exception):
   
    # we add the path to the the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, '404.html')