from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from PIL import Image
from django.utils import timezone
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def custom_authenticate(self, email, password):
        try:
            user = self.get(email=email)
        except self.model.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        print(user)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class UserAbstract(AbstractUser):
    # firstname = models.CharField(max_length=255, blank=True, null=True)
    # lastname = models.CharField(max_length=255, blank=True, null=True)
    about_me = models.TextField(blank=True, null=True, verbose_name='aboutMe')
    email = models.EmailField(verbose_name='email address')
    facebook = models.CharField(max_length=100, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    vk = models.CharField(max_length=100, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)
    youtube = models.CharField(max_length=100, blank=True, null=True)
    github = models.CharField(max_length=100, blank=True, null=True)
    main_link = models.CharField(max_length=100, blank=True, null=True, verbose_name='mainLink')
    looking_for_a_job = models.BooleanField(default=False, verbose_name='Работа')
    looking_for_a_job_description = models.TextField(blank=True, null=True, verbose_name='Описание работы')
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='fullName')
    small_photo_url = models.ImageField(upload_to='profile_photos/small/', blank=True, null=True)
    large_photo_url = models.ImageField(upload_to='profile_photos/large/', blank=True, null=True)
    is_superuser = models.BooleanField(verbose_name='Суперпользователь', default=False)
    is_staff = models.BooleanField(verbose_name='Персонал', default=False)
    status = models.CharField(max_length=150, blank=True, null=True)

    objects = CustomUserManager()  # Используем свой менеджер

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.small_photo_url:
            self.create_small_photo()

    def create_small_photo(self):
        if self.small_photo_url:
            img = Image.open(self.small_photo_url.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.small_photo_url.path)

    @classmethod
    def create_user(cls, email, username, password, full_name):
        user = cls.objects.create_user(email=email, username=username, password=password, full_name=full_name)
        return user

    @classmethod
    def custom_authenticate(cls, email, password):
        user = cls.objects.custom_authenticate(email=email, password=password)
        return user

    def get_user_data_for_response(self):
        return {
            "aboutMe": self.about_me,
            "contacts": {
                "facebook": self.facebook,
                "website": self.website,
                "vk": self.vk,
                "twitter": self.twitter,
                "instagram": self.instagram,
                "youtube": self.youtube,
                "github": self.github,
                "mainLink": self.main_link,
            },
            "lookingForAJob": self.looking_for_a_job,
            "lookingForAJobDescription": self.looking_for_a_job_description,
            "fullName": self.full_name,
            "userId": self.id,
            "photos": {
                "small": self.small_photo_url,
                "large": self.large_photo_url,
            }
        }

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Пользователь Abstract'
        verbose_name_plural = 'Пользователи'


class UserSubscription(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        verbose_name_plural = 'Друзья'


class PostModel(models.Model):
    author = models.ForeignKey(UserAbstract, on_delete=models.CASCADE, related_name='authored_posts')  # Автор поста
    message = models.TextField()  # Текст поста
    like_count = models.PositiveIntegerField(default=0)  # Количество лайков
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    user_post = models.ForeignKey(UserAbstract, models.PROTECT, related_name='posts')  # Пользователь, на чьей странице был оставлен пост
    photo_post_url = models.ImageField(upload_to='post_photo/', blank=True, null=True)

    def __str__(self):
        return f"Post by {self.author.full_name} on {self.user_post.full_name}'s page"

    class Meta:
        verbose_name_plural = 'Посты'


class Like(models.Model):
    user = models.ForeignKey(UserAbstract, on_delete=models.CASCADE)
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Лайки'


class CommentModel(models.Model):
    comment_author = models.ForeignKey(UserAbstract, on_delete=models.CASCADE, related_name='comment_author')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='comments')

    class Meta:
        verbose_name_plural = 'Комментарии'


class MessageModel(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['sender', 'recipient'], name='sender_recipient_idx')
        ]
        ordering = ['-timestamp']

    # def __str__(self):
    #     return f"From {self.sender} to {self.recipient} - {self.timestamp}"

