import django_filters
from django_filters import FilterSet
from django.forms import DateInput
from .models import Post

class NewsFilter(FilterSet):
    datetime = django_filters.DateFilter(
        field_name='datetime',
        lookup_expr='gte',
        widget=DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = Post
        fields = {
            'heading',
            'author',
            'datetime',
            'category'
        }