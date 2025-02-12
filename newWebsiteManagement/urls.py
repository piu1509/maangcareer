from rest_framework.routers import SimpleRouter
from newWebsiteManagement import views
from django.urls import include, path

router = SimpleRouter()

router.register(r'testimonials', views.TestimonialViewSet, 'Testimonial')
router.register(r'mentors', views.MentorViewSet, 'Mentor')
router.register(r'faqs', views.FAQViewSet, 'FAQ')
#all blog list and blog details
router.register(r'blogs', views.BlogViewSet, 'Blog')
# router.register(r'blogs-by-group//<int:group_id>/', views.BlogListByGroupView, 'blogs-by-group')
router.register(r'comments', views.CommentViewSet, basename='Comment')
router.register(r'placement_story_comments', views.PlacementStoryCommentViewSet, basename='Placement_Story_Comment')
router.register(r'placement_story_videos', views.PlacementStoryVideoViewSet, basename='Placement_Story_Video')
router.register(r'media_coverage', views.MediaCoverageViewSet, basename='Media_Coverage')
router.register(r'gallery', views.GalleryViewSet, basename='Gallery')
urlpatterns = [
    path('', include(router.urls)),
    path('blogs-by-group/', views.BlogListByGroupView.as_view({'get': 'list'}), name='blogs-by-group'),
    path('all-group-blogs/', views.GropuOfBlogViewSet.as_view({'get': 'list'}), name='all-group-blogs'),
]
