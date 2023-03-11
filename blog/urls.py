from django.urls import path
from . import views
urlpatterns = [
    path('' , views.post_list , name ='list-post' ),
    path('tag/<slug:tag_slug>/' , views.post_list , name='post-list-by-tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/' , views.detail_post , name='detail-post'),
    path('<int:post_id>/share/' , views.post_share , name='post-share'),
    path('<int:post_id>/comment/' , views.post_comment , name='post-comment'),
    path('search/' , views.post_search , name='post_search'),
]
