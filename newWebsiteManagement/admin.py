from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from .models import *

admin.site.register((
    Testimonial,
    Mentor
))



def copy_faqs(modeladmin, request, queryset):
    for faq in queryset:
        faq.pk = None  # This will create a new instance
        faq.save()
copy_faqs.short_description = "Copy selected FAQs"

def copy_blogs(modeladmin, request, queryset):
    for blog in queryset:
        blog.pk = None  # This will create a new instance
        blog.save()
copy_blogs.short_description = "Copy selected Blogs"

class FAQAdmin(admin.ModelAdmin):
    list_filter = ('group_of_faq',)
    actions = [copy_faqs]

class BlogTopicInline(admin.StackedInline):
    model = BlogTopic
    extra = 1

class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1

class BlogAdmin(admin.ModelAdmin):
    
    inlines = (
        BlogTopicInline,
        CommentInline
    )
    list_filter = ('group_of_blog',)
    actions = [copy_blogs]

admin.site.register(Blog, BlogAdmin)
admin.site.register(GropuOfBlog)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(GroupOfFAQ)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'admin_approval', 'like')
    list_filter = ('date', 'admin_approval')
    search_fields = ('name', 'text')

admin.site.register(PlacementStoryComment)
admin.site.register(PlacementStoryVideo)
admin.site.register(MediaCoverage)
admin.site.register(Gallery)
