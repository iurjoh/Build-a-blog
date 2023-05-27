from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('like/<slug:slug>', views.PostLike.as_view(), name='post_like'),
    path('share/<slug:slug>', views.PostShare.as_view(), name='post_share'),
    path('edit/<slug:slug>/', views.PostEdit.as_view(), name='post_edit'),
    path('delete/<slug:slug>/', views.PostDelete.as_view(), name='post_delete'),
    path('create/<slug:slug>/', views.PostCreate.as_view(), name='post_create'),
]
