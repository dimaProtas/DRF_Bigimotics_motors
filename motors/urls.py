from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework.authtoken.views import obtain_auth_token
from app.views import UserView, AuthMeView, UsersView, StatusView, LogoutView, LoginView, UserProfilePhotoView, \
    RefreshTokenView, FollowView, UnfollowView, UserRegistrationView, PostView, DeletePostView, AddLikeView, \
    FriendsView, MessageListCreateView, UserMessageListView, SendMessageView, CommentsView, NewsAll
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'users', UsersView, basename='users')
router.register(r'news', NewsAll, basename='news')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/music/', include('audio_cloud.urls')),
    path('api/', include('app.urls')),
    path('api/user/<int:pk>/', UserView.as_view(), name='user-detail'),
    path('api/status/<int:pk>/', StatusView.as_view(), name='status-detail'),
    path('api/auth/login/', LoginView.as_view({'post': 'create'}), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='api-logout'),
    path('api/photo/', UserProfilePhotoView.as_view(), name='api-photo'),
    path('api/', include(router.urls)),
    path('api/register/', UserRegistrationView.as_view(), name='user-register'),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', views.obtain_auth_token),
    path('api/auth/me', AuthMeView, name='auth-me'),
    path('api/token/refresh/', RefreshTokenView.as_view(), name='token-refresh'),
    path('api/follow/<int:user_id>/', FollowView.as_view(), name='follow-user'),
    path('api/unfollow/<int:user_id>/', UnfollowView.as_view(), name='unfollow-user'),
    path('api/user/post/<int:user_id>/', PostView.as_view({'get': 'list', 'post': 'create'}), name='user-post'),
    path('api/user/post/<int:post_id>/delete/', DeletePostView.as_view(), name='delete-post'),
    path('api/user/post/like/<int:post_id>/', AddLikeView.as_view()),
    path('api/friends/', FriendsView.as_view({'get': 'list'})),
    path('api/messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('api/messages/<int:user_id>/', UserMessageListView.as_view({'get': 'list'}), name='user-message-list'),
    path('api/send-message/', SendMessageView.as_view(), name='send-message'),
    path('api/post/comments/', CommentsView.as_view({'get': 'list', 'post': 'create'})),
    path('api/comments/<int:pk>/delete/', CommentsView.as_view({'delete': 'delete_comment'}), name='delete-comment'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
