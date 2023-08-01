from urllib import request
from django.shortcuts import render
from .forms import ContactForm
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages


from webapp.models import Aboutfield, Pack, Testimonial, Feature, Blog

# Create your views here.
def home(request):
    # pack = Pack.objects.all()
    testimonials = Testimonial.objects.all() 
    aboutfields = Aboutfield.objects.all()
    featurelist = Feature.objects.all()  
    packs = Pack.objects.all()
    blogs = Blog.objects.all()
    context = {'testimonials': testimonials, 'aboutfields':aboutfields, 'packs':packs, 'featurelist':featurelist, 'blogs':blogs}
    return render (request, 'webapp/homepage.html', context)  #Contxt to load data fron database to tte page

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid(): 
            user =form.save()
            # message1 = user.name, user.email, user.message, user.phone, user.mode_of_contact     
            context = {'user': user}  
            form.save()
            html_template = 'email_template.html'
            html_message = render_to_string(html_template, context)
            subject = "Thank you for contacting us"
            message = "Hi " + user.name + " ,we will contact you in your number " + user.phone 
            email_from = settings.EMAIL_HOST_USER
            email = form.cleaned_data['email']
            recipient_list =[email]
            # recipient_admin =
            message = EmailMessage(subject, html_message,
                                   email_from, recipient_list)
            message.content_subtype = 'html'
            try:
                message.send()
            except BadHeaderError:
                return HttpResponse("Invalid header found.") 
            # send_mail(subject, message1, email_from, 'humagain.binay@gmail.com')
            messages.success(request, 'Your feedback has been sent. Please check email for confirmation')
            return render(request, 'webapp/contact.html') 
    form = ContactForm()
    context = {'form': form}
    return render(request, 'webapp/contact.html', context)

def about(request):
    testimonials = Testimonial.objects.all()
    aboutfields = Aboutfield.objects.all()
    context = {'testimonials':testimonials, 'aboutfields':aboutfields}
    return render(request, 'webapp/about.html', context)