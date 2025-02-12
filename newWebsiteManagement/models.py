from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Testimonial(models.Model):
    name = models.CharField(max_length=35)
    text = models.CharField(max_length=256)
    date = models.DateField()
    photo = models.ImageField(upload_to='testimonials')
    university = models.CharField(max_length=255, null=True, blank=True)
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
    comment = models.TextField(null=True, blank=True)

    def __str__(self) -> str:return self.name

class GroupOfFAQ(models.Model):
    group_name = models.CharField(max_length=255)

    def __str__(self):
        return self.group_name

class FAQ(models.Model):
    group_of_faq = models.ForeignKey(GroupOfFAQ, on_delete=models.CASCADE, related_name='faqs', null=True, blank=True)
    question = models.CharField(max_length=100)
    answer = models.TextField()

    def __str__(self) -> str:return f"{self.question[:30]}..." if len(self.question) > 30 else self.question

###############

class GropuOfBlog(models.Model):
    group_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.group_name

class Blog(models.Model):
    group_of_blog = models.ForeignKey(GropuOfBlog, on_delete=models.CASCADE, related_name="blogs", null=True, blank=True)
    title = models.CharField(max_length=256)
    text = models.TextField()
    date = models.DateField()
    introduction = models.TextField(null=True, blank=True)
    written_by = models.CharField(max_length=100, null=True, blank=True)
    written_at = models.DateTimeField(null=True, blank=True)
    photo = models.ImageField(upload_to='blogs')
    popular = models.BooleanField(default=False)
    read_time = models.CharField(max_length=5, help_text='please input the number only; eg -> 5')
    views = models.BigIntegerField(default=0)
    like = models.BigIntegerField(default=0)

    @property
    def count_comments(self):
        return self.comment_set.count()

    def __str__(self) -> str:
        return f"{self.title[:30]}..." if len(self.title) > 30 else self.title

  
############

class BlogTopic(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=100)
    text = models.TextField()

    def __str__(self) -> str:return self.title

class Comment(models.Model):
    name = models.CharField(max_length=35)
    text = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    admin_approval = models.BooleanField(default=False)
    like = models.BigIntegerField(default=0)
    def __str__(self) -> str:return f"{self.name[:30]}..." if len(self.name) > 30 else self.name

############ New Add ##############

class PlacementStoryComment(models.Model):
    name = models.CharField(max_length=255)
    company_and_role = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='placement_stories/comments/')
    linked_in_link = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class PlacementStoryVideo(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    company_and_role = models.CharField(max_length=255, null=True, blank=True)
    thumbnail = models.ImageField(upload_to='placement_story/videos/')
    video_link = models.FileField(upload_to='placement_story/videos/')
    text = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class MediaCoverage(models.Model):
    media_name = models.CharField(max_length=255)
    date = models.DateField()
    caption = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='media_coverage/', null=True, blank=True)
    news_link = models.URLField()
    media_logo = models.ImageField(upload_to='media_coverage/', null=True, blank=True)

    def __str__(self):
        return self.media_name
    
class Gallery(models.Model):
    image = models.ImageField(upload_to='gallery/')

    def __str__(self):
        return f'Gallery Image {self.pk}'