from django.db.models import Q
from rest_framework import viewsets
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import logout
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.viewsets import ViewSet
from rest_framework.pagination import LimitOffsetPagination
from .serializers import UserModelSerializerBase, UsersSerializer, StatusSerializer, \
    UserRegistrationSerializer, PostSerializer, PostSerializerPost, MessageSerializerBase, \
    SendMessageSerializer, CommentsSerializer
from .models import UserAbstract, UserSubscription, PostModel, Like, MessageModel, CommentModel
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action


class CommentsView(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer

    def get_queryset(self):
        queryset = CommentModel.objects.all()
        return queryset

    def perform_create(self, serializer):
        post_id = self.request.data['post']  # Получаем id поста из запроса

        try:
            post = PostModel.objects.get(id=post_id)
        except PostModel.DoesNotExist:
            raise serializers.ValidationError("Invalid post ID")

        serializer.save(comment_author=self.request.user, post=post)

    @action(detail=True, methods=['DELETE'])
    def delete_comment(self, request, pk=None):
        try:
            comment = CommentModel.objects.get(id=pk)
        except CommentModel.DoesNotExist:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        # Проверьте, имеет ли пользователь право на удаление этого комментария, например:
        if comment.comment_author != self.request.user:
            return Response({"detail": "You don't have permission to delete this comment"}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddLikeView(APIView):
    def post(self, request, post_id):
        try:
            post = PostModel.objects.get(pk=post_id)
        except PostModel.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user  # Получаем текущего пользователя

        # Проверяем, что пользователь еще не поставил лайк
        if not Like.objects.filter(user=user, post=post).exists():
            post.like_count += 1
            post.save()

            # Создаем новую запись в модели Like
            like = Like(user=user, post=post)
            like.save()

            response_data = {
                'resultCode': 0,
                'messages': ['Like added successfully'],
                'data': {}
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Post is already liked'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        try:
            post = PostModel.objects.get(pk=post_id)
        except PostModel.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user  # Получаем текущего пользователя

        # Проверяем, что пользователь уже поставил лайк
        try:
            like = Like.objects.get(user=user, post=post)
            like.delete()  # Удаляем запись из модели Like
            if post.like_count > 0:
                post.like_count -= 1
                post.save()
                response_data = {
                    'resultCode': 0,
                    'messages': ['Like removed successfully'],
                    'data': {}
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'No likes to remove'}, status=status.HTTP_400_BAD_REQUEST)
        except Like.DoesNotExist:
            return Response({'error': 'Like not found'}, status=status.HTTP_400_BAD_REQUEST)


class PostView(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser, FormParser)
    def get_serializer_class(self):
        if self.action == 'create':
            return PostSerializerPost
        return PostSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Добавляем нужные данные в контекст, например, текущего пользователя
        context['request'] = self.request
        return context

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        queryset = PostModel.objects.filter(user_post=user_id)
        return queryset

    def perform_create(self, serializer):
        author_id = int(self.request.data['author'])
        user_post_id = self.request.data['user_post']
        photo_post = self.request.FILES.get('photo_post_url')  # Получаем загруженный файл

        try:
            author = UserAbstract.objects.get(id=author_id)
        except UserAbstract.DoesNotExist:
            raise serializers.ValidationError("Invalid author ID")

        try:
            user_post = UserAbstract.objects.get(id=user_post_id)
        except UserAbstract.DoesNotExist:
            raise serializers.ValidationError("Invalid user_post ID")

        serializer.validated_data['author'] = author
        serializer.save(user_post=user_post, photo_post_url=photo_post)


class DeletePostView(APIView):
    def delete(self, request, post_id):
        try:
            post = PostModel.objects.get(pk=post_id)
        except PostModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRegistrationView(APIView):
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = UserAbstract.custom_authenticate(email=request.data['email'], password=request.data['password'])
            if user:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                request.session['access_token'] = access_token
                request.session['refresh_token'] = refresh_token

                response_data = {
                    'resultCode': 0,
                    'messages': ["User registered successfully."],
                    'data': {
                        'userId': user.id,
                        'token': access_token,
                        'refreshToken': refresh_token,
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'resultCode': 1,
                    'messages': ['Something went wrong'],
                    'data': {},
                }
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_200_OK)


class UserProfilePhotoView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, *args, **kwargs):
        user = request.user
        photo = request.data.get('image')

        # Произведите обработку фото, уменьшите размер, если это необходимо
        # Сохраните оригинальное фото в поле large_photo_url
        user.large_photo_url = photo
        user.small_photo_url = photo

        try:
            user.save()
            user.create_small_photo()
            user.save()

            small_photo_url = user.small_photo_url.url if user.small_photo_url else None
            large_photo_url = user.large_photo_url.url if user.large_photo_url else None

            base_url = settings.MEDIA_URL
            if large_photo_url:
                large_photo_url = large_photo_url.replace(settings.MEDIA_ROOT, base_url)
            if small_photo_url:
                small_photo_url = small_photo_url.replace(settings.MEDIA_ROOT, base_url)

            return Response({
                'resultCode': 0,
                'messages': [],
                'data': {
                    'photos': {
                        'small': self.request.build_absolute_uri(small_photo_url) if small_photo_url else None,
                        'large': self.request.build_absolute_uri(large_photo_url) if large_photo_url else None,
                    },
                },
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'resultCode': 1,
                'messages': ['Something went wrong'],
                'data': {},
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserView(RetrieveUpdateAPIView):
    queryset = UserAbstract.objects.all()
    serializer_class = UserModelSerializerBase

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Обновление полей напрямую
        instance.about_me = request.data.get('aboutMe')
        instance.username = request.data.get('login')
        instance.looking_for_a_job = request.data.get('lookingForAJob')
        instance.looking_for_a_job_description = request.data.get('lookingForAJobDescription')
        instance.full_name = request.data.get('fullName')
        instance.main_link = request.data.get('mainLink')

        # Обновление полей контактов
        contacts_fields = ['facebook', 'website', 'vk', 'twitter', 'instagram', 'youtube', 'github']
        for field in contacts_fields:
            setattr(instance, field, request.data.get(field))

        instance.save()

        try:
            return Response({
                'resultCode': 0,
                'messages': [],
                'data': {},
            })
        except Exception as e:
            return Response({
                'resultCode': 1,
                'messages': ['Something wrong'],
                'data': {},
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UsersLimitOffSetPagination(LimitOffsetPagination):
    default_limit = 5

class UsersView(viewsets.ReadOnlyModelViewSet):
    queryset = UserAbstract.objects.all()
    serializer_class = UsersSerializer
    pagination_class = UsersLimitOffSetPagination


class FriendsView(viewsets.ReadOnlyModelViewSet):
    serializer_class = UsersSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        request_user = self.request.user
        return UserAbstract.objects.filter(followers__from_user=request_user)


class StatusView(RetrieveUpdateAPIView):
    queryset = UserAbstract.objects.all()
    serializer_class = StatusSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_update(serializer)
            return Response({
                'resultCode': 0,
                'messages': [],
                'data': {},
            })
        except Exception as e:
            return Response({
                'resultCode': 1,
                'messages': ['Something wrong'],
                'data': {},
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def AuthMeView(request):
    user = request.user

    if user.is_authenticated:
        data = {
            'data': {
                'id': user.id,
                'login': user.username,
                'email': user.email,
            },
            'messages': [],
            'fieldsErrors': [],
            'resultCode': 0
        }
    else:
        data = {
            'data': {},
            'messages': ['You are not authorized'],
            'fieldsErrors': [],
            'resultCode': 1
        }

    return Response(data, status=status.HTTP_200_OK)


class LoginView(ViewSet):
    def create(self, request, *args, **kwargs):  # Это метод, который обработает POST-запрос
        email = request.data.get('email')
        password = request.data.get('password')

        user = UserAbstract.custom_authenticate(email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Добавляем отладочный вывод
            # print('Access token saved:', access_token)
            # print('Refresh token saved:', refresh_token)

            # Сохраняем токены в localStorage
            request.session['access_token'] = access_token
            request.session['refresh_token'] = refresh_token

            return Response({
                'resultCode': 0,
                'messages': [],
                'data': {
                    'userId': user.id,
                    'token': access_token,
                    'refreshToken': refresh_token,  # Добавляем refreshToken в ответ
                }
            })
        else:
            return Response({
                'resultCode': 1,
                'messages': ['Invalid credentials'],
                'data': {}
            }, status=status.HTTP_200_OK)


class RefreshTokenView(TokenRefreshView):
    pass


class LogoutView(APIView):
    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response({
            'resultCode': 0,
            'messages': [],
            'data': {}
        })


class FollowView(APIView):
    def post(self, request, user_id):
        from_user = request.user
        to_user = UserAbstract.objects.get(pk=user_id)  # Получение пользователя, на которого подписываемся

        if from_user != to_user:
            subscription, created = UserSubscription.objects.get_or_create(from_user=from_user, to_user=to_user)
            if created:
                data = {
                    'resultCode': 0,
                    'messages': [],
                    'data': {}
                }
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                data = {
                    'resultCode': 1,
                    'messages': ['User already followed'],
                    'data': {}
                }
                return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                'resultCode': 2,
                'messages': ['You cannot follow yourself'],
                'data': {}
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class UnfollowView(APIView):
    def delete(self, request, user_id):
        from_user = request.user
        to_user = UserAbstract.objects.get(pk=user_id)  # Получение пользователя, от которого отписываемся

        subscription = UserSubscription.objects.filter(from_user=from_user, to_user=to_user).first()
        if subscription:
            subscription.delete()
            data = {
                'resultCode': 0,
                'messages': [],
                'data': {}
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                'resultCode': 1,
                'messages': ['Subscription not found'],
                'data': {}
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializerBase
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return MessageModel.objects.all()
        # return MessageModel.objects.filter(sender=user) | MessageModel.objects.filter(recipient=user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class UserMessageLimitOffSetPagination(LimitOffsetPagination):
    default_limit = 10


class UserMessageListView(viewsets.ModelViewSet):
    serializer_class = MessageSerializerBase
    pagination_class = UserMessageLimitOffSetPagination
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        other_user_id = self.kwargs.get('user_id')
        other_user = get_object_or_404(UserAbstract, id=other_user_id)

        # Получить все сообщения между текущим пользователем и другим пользователем
        queryset = MessageModel.objects.filter(
            (Q(sender=current_user) & Q(recipient=other_user)) |
            (Q(sender=other_user) & Q(recipient=current_user))
        ).order_by('-timestamp')
        print(queryset, '---------- queryset')
        if queryset:
            return queryset
        else:
            return []


class SendMessageView(APIView):
    def post(self, request):
        serializer = SendMessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            data = {
                'resultCode': 0,
                'messages': [],
                'data': {}
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
