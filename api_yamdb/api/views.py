from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import AdminOnly, ReadAnyWriteAdmin, SpecialPermission
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          OwnUserSerializer, ReviewSerializer,
                          SingUpSerializer, TitleReadSerializer,
                          TitleWriteSerializer, UserSerializer)


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (ReadAnyWriteAdmin,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (ReadAnyWriteAdmin,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (ReadAnyWriteAdmin,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer

    def perform_create(self, serializer):
        request = dict(self.request.data)
        genre = Genre.objects.filter(
            slug__in=request.get('genre'))
        if not genre:
            raise AttributeError
        category = Category.objects.get(slug=self.request.data.get('category'))
        serializer.save(category=category, genre=list(genre))

    def perform_update(self, serializer):
        category = Category.objects.get(slug=self.request.data.get('category'))
        genre_slugs = self.request.data.get('genre')
        if not genre_slugs:
            genre = []
        else:
            genre = Genre.objects.filter(
                slug__in=self.request.data.get('genre'))
        serializer.save(category=category, genre=genre)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (SpecialPermission,)

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, id=review_id)
        queryset = review.comments.all()
        return queryset

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        serializer.save(
            author=self.request.user,
            review_id=review.id
        )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (SpecialPermission,)

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        queryset = title.reviews.all()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        if self.request.user.reviews.filter(title=title.id).count():
            return Response(
                {'author': 'Отзыв от данного автора уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title_id=self.kwargs.get("title_id")
        )


class SingUpView(APIView):

    def post(self, request):
        serializer = SingUpSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create(
                username=serializer.data['username'],
                email=serializer.data['email']
            )
            token = default_token_generator.make_token(user=user)
            send_mail(
                'SingUp in Yamdb',
                f'Confirmation code: {token}',
                'post@mail.ru',
                [user.email, ]
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTokenView(APIView):

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(
                User,
                username=serializer.data['username']
            )
            if default_token_generator.check_token(
                user=user,
                token=serializer.data['confirmation_code']
            ):
                access = AccessToken.for_user(user)
                data = {'token': str(access)}
                return Response(data, status=status.HTTP_200_OK)
            data = {
                'confirmation_code': 'Указан неверный код подтверждения',
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'username'

    @action(
        methods=['get', 'patch'],
        detail=False,
        serializer_class=OwnUserSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
