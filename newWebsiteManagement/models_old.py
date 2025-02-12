from django.db import models

# Create your models here.
class Testimonial(models.Model):
    name = models.CharField(max_length=35)
    text = models.CharField(max_length=256)
    date = models.DateField()
    photo = models.ImageField(upload_to='testimonials')
    stars = models.CharField(max_length=2, choices=(
        ('0', '0 Stars'),
        ('1', '0.5 Stars'),
        ('2', '1 Star'),
        ('3', '1.5 Stars'),
        ('4', '2 Stars'),
        ('5', '2.5 Stars'),
        ('5', '2.5 Stars'),
        ('6', '3 Stars'),
        ('7', '3.5 Stars'),
        ('8', '4 Stars'),
        ('9', '4.5 Stars'),
        ('10', '5 Stars'),
    ))

    def __str__(self) -> str:return self.name

class Mentor(models.Model):
    name = models.CharField(max_length=35)
    subtext = models.CharField(max_length=50)
    maintext = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='mentors')

    def __str__(self) -> str:return self.name

class FAQ(models.Model):
    question = models.CharField(max_length=100)
    answer = models.TextField()

    def __str__(self) -> str:return f"{self.question[:30]}..." if len(self.question) > 30 else self.question

class Blog(models.Model):pass