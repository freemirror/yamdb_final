from csv import DictReader

from django.core.management import BaseCommand
from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)


class Command(BaseCommand):

    help = 'Load data from .csv files'

    def handle(self, *args, **kwds):
        print('Loading data from .csv files')

        for row in DictReader(
            open('static/data/category.csv', encoding="utf-8")
        ):
            category = Category(name=row['name'], slug=row['slug'])
            category.save()
        print('category.csv uploaded')

        for row in DictReader(open('static/data/genre.csv', encoding="utf-8")):
            genre = Genre(name=row['name'], slug=row['slug'])
            genre.save()
        print('genre.csv uploaded')

        for row in DictReader(
            open('static/data/titles.csv', encoding="utf-8")
        ):
            title = Title(
                name=row['name'],
                year=row['year'],
                category=Category.objects.get(pk=row['category'])
            )
            title.save()
        print('titles.csv uploaded')

        for row in DictReader(
            open('static/data/genre_title.csv', encoding="utf-8")
        ):
            genre_title = GenreTitle(
                title=Title.objects.get(pk=row['title_id']),
                genre=Genre.objects.get(pk=row['genre_id'])
            )
            genre_title.save()
        print('genre_title.csv uploaded')

        for row in DictReader(
            open('static/data/users.csv', encoding="utf-8")
        ):
            user = User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                role=row['role'],
                bio=row['bio'],
                first_name=row['first_name'],
                last_name=row['last_name']
            )
            user.save()
        print('user.csv uploaded')

        for row in DictReader(
            open('static/data/review.csv', encoding="utf-8")
        ):
            review = Review(
                title=Title.objects.get(pk=row['title_id']),
                text=row['text'],
                author=User.objects.get(pk=row['author']),
                score=row['score'],
                pub_date=row['pub_date']
            )
            review.save()
        print('review.csv uploaded')

        for row in DictReader(
            open('static/data/comments.csv', encoding="utf-8")
        ):
            comment = Comment(
                review=Review.objects.get(pk=row['review_id']),
                text=row['text'],
                author=User.objects.get(pk=row['author']),
                pub_date=row['pub_date']
            )
            comment.save()
        print('comments.csv uploaded')

        print('all .csv files have been uploaded')
