from django.shortcuts import get_object_or_404
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from .models import UserAbstract, UserSubscription, PostModel, Like, MessageModel, CommentModel
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    repidPassword = serializers.CharField(write_only=True)

    class Meta:
        model = UserAbstract
        fields = ('full_name', 'email', 'username', 'password', 'repidPassword')

    def validate(self, data):
        if data['password'] != data['repidPassword']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        repid_password = validated_data.pop('repidPassword')
        print(validated_data)
        user = UserAbstract.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            full_name=validated_data['full_name']
        )

        user.set_password(repid_password)
        user.save()
        return user



class UserModelSerializerBase(serializers.ModelSerializer):
    contacts = serializers.SerializerMethodField()
    aboutMe = serializers.CharField(source='about_me')
    lookingForAJob = serializers.BooleanField(source='looking_for_a_job')
    lookingForAJobDescription = serializers.CharField(source='looking_for_a_job_description')
    fullName = serializers.CharField(source='full_name')
    userId = serializers.IntegerField(source='id')
    photos = serializers.SerializerMethodField()

    class Meta:
        model = UserAbstract
        fields = ['aboutMe', 'contacts', 'lookingForAJob', 'lookingForAJobDescription',
                  'fullName', 'userId', 'photos', 'username']


    def get_contacts(self, obj):
        return {
            'facebook': obj.facebook,
            'website': obj.website,
            'vk': obj.vk,
            'twitter': obj.twitter,
            'instagram': obj.instagram,
            'youtube': obj.youtube,
            'github': obj.github,
            'mainLink': obj.main_link,
        }

    def get_photos(self, obj):
        return {
            "small": self.context['request'].build_absolute_uri(obj.small_photo_url.url) if obj.small_photo_url else None,
            "large": self.context['request'].build_absolute_uri(obj.large_photo_url.url) if obj.large_photo_url else None,
        }

    # def update(self, instance, validated_data):
    #     contacts_data = validated_data.pop('contacts', {})  # Извлечь данные о контактах
    #     instance = super().update(instance, validated_data)  # Вызвать метод update базового класса
    #     print('contacts_data', '\n---------------\n', contacts_data)
    #     # Обновить данные о контактах
    #     for key, value in contacts_data.items():
    #         setattr(instance, key, value)
    #
    #     instance.save()
    #     print('instance', '\n---------------\n', instance)
    #     return instance


class StatusSerializer(serializers.Serializer):
    status = serializers.CharField()

    class Meta:
        model = UserAbstract
        fields = ['status']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class UsersSerializer(serializers.Serializer):
    name = serializers.CharField(source='full_name')
    id = serializers.IntegerField()
    photos = serializers.SerializerMethodField()
    status = serializers.CharField()
    followed = serializers.SerializerMethodField()

    def get_followed(self, instance):
        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return instance.followers.filter(from_user=request_user).exists()
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def get_photos(self, obj):
        if obj.small_photo_url and obj.large_photo_url:
            request = self.context.get('request')
            small_photo_url = request.build_absolute_uri(obj.small_photo_url.url)
            large_photo_url = request.build_absolute_uri(obj.large_photo_url.url)
            return {
                "small": small_photo_url,
                "large": large_photo_url,
            }
        return {
            "small": None,
            "large": None,
        }

    class Meta:
        model = UserAbstract
        fields = ['name', 'id', 'status', 'followed', 'photos']



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    rememberMe = serializers.BooleanField(required=False)
    # captcha = serializers.CharField(required=False)


class UserSubscriptionSerializer(serializers.ModelSerializer):
    followed = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = '__all__'

    def get_followed(self, obj):
        request_user_id = self.context['request'].user.id
        return obj.to_user_id == request_user_id  # Проверяем, подписан ли текущий пользователь на этого пользователя


# class PostSerializer(ModelSerializer):
#     author = UsersSerializer()
#
#     class Meta:
#         model = PostModel
#         fields = ['id', 'author', 'message', 'like_count', 'created_at', 'user_post']

class PostSerializer(serializers.ModelSerializer):
    author = UsersSerializer()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = PostModel
        fields = ['id', 'author', 'message', 'like_count', 'created_at', 'user_post', 'is_liked', 'photo_post_url']

    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            try:
                like = Like.objects.get(user=user, post=obj)
                return True
            except Like.DoesNotExist:
                return False
        return False

class PostSerializerPost(ModelSerializer):
    # author = UsersSerializer()

    class Meta:
        model = PostModel
        fields = ['id', 'author', 'message', 'like_count', 'created_at', 'user_post', 'photo_post_url']


class CommentsSerializer(ModelSerializer):
    comment_author = UsersSerializer(read_only=True)  # Указываем read_only=True
    class Meta:
        model = CommentModel
        fields = ['id', 'comment_author', 'message', 'created_at', 'post']
        read_only_fields = ['comment_author']  # Указываем comment_author как read-only


class MessageSerializerBase(ModelSerializer):
    class Meta:
        model = MessageModel
        fields = ['id', 'sender', 'recipient', 'text', 'timestamp']


class SendMessageSerializer(serializers.Serializer):
    recipient = serializers.PrimaryKeyRelatedField(queryset=UserAbstract.objects.all())
    text = serializers.CharField()

    def create(self, validated_data):
        sender = self.context['request'].user
        recipient = validated_data['recipient']
        text = validated_data['text']
        message = MessageModel.objects.create(sender=sender, recipient=recipient, text=text)
        return message