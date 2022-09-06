import datetime as dt
import re

from django.db.models import Avg
from rest_framework import serializers

from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
        )
        model = Title

    def get_rating(self, obj):
        value = Review.objects.filter(
            title=obj.id
        ).aggregate(rating=Avg('score'))
        return value['rating']


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )
        model = Title

    def create(self, validated_data):
        genres = list(validated_data.pop('genre'))
        title = Title.objects.create(**validated_data)
        for genre in genres:
            GenreTitle.objects.create(genre=genre, title=title,)
        return title

    def update(self, instance, validated_data):
        genres = list(validated_data.pop('genre'))
        title = Title.objects.filter(id=instance.id)
        title.update(**validated_data)
        genre_titles = GenreTitle.objects.filter(title_id=instance.id)
        genre_titles.delete()
        for genre in genres:
            GenreTitle.objects.create(genre=genre, title=title[0])
        return title[0]

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError('Проверьте год рождения!')
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate_score(self, value):
        if value in range(1, 11):
            return value
        raise serializers.ValidationError(
            'Оценка произведения должна находится в пределах от 1 до 10'
        )


class ValidateFunctions:

    def validate_username(self, value):
        if User.objects.filter(username=value).count():
            raise serializers.ValidationError(
                'Указанное имя пользователя уже существует.'
            )
        elif value == 'me':
            raise serializers.ValidationError(
                'Использовать имя me в качестве username запрещено.'
            )
        elif not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'В username используются запрещенные символы'
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).count():
            raise serializers.ValidationError(
                'Указанный email уже существует.'
            )
        elif not re.match(r'[^@\s]+@[^@\s]+\.[^@\s]+', value):
            raise serializers.ValidationError(
                'Некоректный адресс e-mail'
            )
        return value


class UserSerializer(serializers.ModelSerializer, ValidateFunctions):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class OwnUserSerializer(serializers.ModelSerializer, ValidateFunctions):
    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(max_length=254, required=False)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class SingUpSerializer(serializers.Serializer, ValidateFunctions):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()
