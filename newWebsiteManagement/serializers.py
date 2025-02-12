from rest_framework.serializers import ModelSerializer
from newWebsiteManagement.models import *


class TestimonialSerializer(ModelSerializer):

    class Meta:
        model = Testimonial
        fields = '__all__'


class MentorSerializer(ModelSerializer):

    class Meta:
        model = Mentor
        fields = '__all__'


class FAQSerializer(ModelSerializer):

    class Meta:
        model = FAQ
        fields = '__all__'

####RijuDjango
class BlogListSerializer(ModelSerializer):

    class Meta:
        model = Blog
        fields = "__all__"



class BlogTopicSerialzer(ModelSerializer):
    class Meta:
        model = BlogTopic
        fields = '__all__'

class CommentSerialzer(ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

    def to_representation(self, instance):
        # Only serialize the comment if it has admin_approval
        if not instance.admin_approval:
            pass
        else:
            return super().to_representation(instance)
        

class BlogSerializer(ModelSerializer):

    comments = CommentSerialzer(many=True)
    topics = BlogTopicSerialzer(many=True)

    class Meta:
        model = Blog
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Filter out None values from comments
        representation['comments'] = [comment for comment in representation['comments'] if comment is not None]
        return representation


class GropuOfBlogSerializer(ModelSerializer):
    
    class Meta:
        model = GropuOfBlog
        fields = ['id', 'group_name']


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['admin_aproval', 'like', 'date']


class PlacementStoryCommentSerializer(ModelSerializer):
    class Meta:
        model = PlacementStoryComment
        fields = ['id', 'name', 'company_and_role', 'text', 'photo', 'linked_in_link']


class PlacementStoryVideoSerializer(ModelSerializer):
    class Meta:
        model = PlacementStoryVideo
        fields = ['id', 'name', 'company_and_role', 'thumbnail', 'video_link', 'text']


class MediaCoverageSerializer(ModelSerializer):
    class Meta:
        model = MediaCoverage
        fields = ['id', 'media_name', 'date', 'caption', 'description', 'thumbnail', 'news_link', 'media_logo']


class GallerySerializer(ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['id', 'image']
        