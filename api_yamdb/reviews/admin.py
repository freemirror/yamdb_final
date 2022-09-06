from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'category')
    search_fields = ('name',)
    list_filter = ('year', 'category', 'genre')
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'text', 'author', 'score', 'pub_date',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'review', 'text', 'author', 'pub_date',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'email',
        'password',
        'is_staff',
        'is_superuser',
        'bio',
        'role'
    )
    list_display_links = ('username',)
    list_editable = ('role',)
