from django.db import models

# Create your models here.
class Testimonial(models.Model):
    name = models.CharField(max_length=50)
    desc = models.TextField()
    designation = models.CharField(default='Officer', max_length=50)

    def __str__(self):
        return self.name

class Aboutfield(models.Model):
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=300)
    
    def __str__(self):
        return self.name

class Feature(models.Model):
    desc = models.CharField(max_length=200)

    def __str__(self):
        return self.desc

class Pack(models.Model):
    id = models.IntegerField
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=200)
    featurelist = models.ManyToManyField(Feature,related_name='featurelist', default='feature1')
    price = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Blog(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField()
    image = models.ImageField()

    def __str__(self):
        return self.name

class Contact(models.Model):
    name = models.CharField(max_length=250)
    email = models.EmailField()
    subject = models.CharField(max_length=50, default='Computer science')
    # mode_of_contact = models.CharField('Conatct by', max_length=50, default='aaa')
    # question_categories = models.CharField('How can we help you?', max_length=50, default='bbb')
    phone = models.CharField(max_length=10, default='ccc')
    message = models.TextField(max_length=3000, default='ddd')

    def __str__(self):
        return self.email