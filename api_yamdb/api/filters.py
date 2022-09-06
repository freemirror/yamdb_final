import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    category = django_filters.AllValuesFilter(field_name='category__slug')
    genre = django_filters.AllValuesFilter(field_name='genre__slug')
    name = django_filters.CharFilter(lookup_expr='gt')

    class Meta:
        model = Title
        fields = ('year', 'name', 'category', 'genre')
