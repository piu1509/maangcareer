from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from newWebsiteManagement.serializers import *
from newWebsiteManagement.models import *
from rest_framework import viewsets, pagination, status
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Or use the PAGE_SIZE from settings
    page_size_query_param = 'page_size'
    max_page_size = 100

class TestimonialViewSet(ViewSet):

    def list(self, request):
        queryset = Testimonial.objects.order_by('pk')
        serializer = TestimonialSerializer(queryset, many=True)
        return Response(serializer.data)

class MentorViewSet(ViewSet):

    def list(self, request):
        queryset = Mentor.objects.order_by('pk')
        serializer = MentorSerializer(queryset, many=True)
        return Response(serializer.data)

class FAQViewSet(ViewSet):

    def list(self, request):
        queryset = FAQ.objects.order_by('pk')
        serializer = FAQSerializer(queryset, many=True)
        return Response(serializer.data)


class BlogViewSet(viewsets.ViewSet):
    pagination_class = StandardResultsSetPagination

    def list(self, request):
        queryset = Blog.objects.order_by('pk')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = BlogListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = BlogListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Blog.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        item.views += 1
        item.save()
        serializer = BlogSerializer(item)
        return Response(serializer.data)

from django.db.models import Q
class BlogListByGroupView(viewsets.ViewSet):
    pagination_class = StandardResultsSetPagination

    def list(self, request):
        group_id = request.GET.get("group_id")
        search_text = request.GET.get("search_text")
        queryset = Blog.objects.filter(group_of_blog_id=group_id)
        if search_text:
            queryset = queryset.filter(Q(title__icontains = search_text))
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = BlogSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = BlogSerializer(queryset, many=True)
        return Response(serializer.data)

class GropuOfBlogViewSet(viewsets.ModelViewSet):
    queryset = GropuOfBlog.objects.all()
    serializer_class = GropuOfBlogSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

class PlacementStoryCommentViewSet(viewsets.ModelViewSet):

    def list(self, request):
        queryset = PlacementStoryComment.objects.order_by('pk')
        serializer = PlacementStoryCommentSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
class PlacementStoryVideoViewSet(viewsets.ModelViewSet):

    def list(self, request):
        queryset = PlacementStoryVideo.objects.order_by('pk')
        serializer = PlacementStoryVideoSerializer(queryset, many=True)
        return Response(serializer.data)
    

class MediaCoverageViewSet(viewsets.ModelViewSet):

    def list(self, request):
        queryset = MediaCoverage.objects.order_by('pk')
        serializer = MediaCoverageSerializer(queryset, many=True)
        return Response(serializer.data)
    

class GalleryViewSet(viewsets.ModelViewSet):

    def list(self, request):
        queryset = Gallery.objects.order_by('pk')
        serializer = GallerySerializer(queryset, many=True)
        return Response(serializer.data)
    