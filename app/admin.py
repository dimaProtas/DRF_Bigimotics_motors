from django.contrib import admin
from app.models import UserAbstract, UserSubscription, PostModel, Like, MessageModel, CommentModel


class UserAbstractAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'status', 'email',
                    'looking_for_a_job', 'looking_for_a_job_description',
                    'is_superuser', 'is_staff']
    list_display_links = ['id', 'email']


class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_user', 'to_user', 'created_at']
    list_display_links = ['id']


class PostModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'message', 'like_count', 'user_post', 'photo_post_url']
    list_display_links = ['id']


class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post']
    list_display_links = ['id']


class MessagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'recipient', 'text', 'timestamp']


class CommentsAdmin(admin.ModelAdmin):
    list_display = ['id', 'comment_author', 'message', 'created_at', 'post']


admin.site.register(UserAbstract, UserAbstractAdmin)
admin.site.register(UserSubscription, UserSubscriptionAdmin)
admin.site.register(PostModel, PostModelAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(MessageModel, MessagesAdmin)
admin.site.register(CommentModel, CommentsAdmin)
