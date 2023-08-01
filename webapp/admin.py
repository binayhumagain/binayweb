from importlib.resources import Package
from django.contrib import admin

# Register your models here.
from .models import Aboutfield, Testimonial, Pack, Feature, Blog, Contact

admin.site.register(Testimonial)
admin.site.register(Aboutfield)
admin.site.register(Pack)
admin.site.register(Feature)
admin.site.register(Blog)
admin.site.register(Contact)