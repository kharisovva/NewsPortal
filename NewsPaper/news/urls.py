from django.urls import path
from .views import NewsList, NewsDetail, PostCreate, PostEdit, PostDelete

urlpatterns = [
   path('', NewsList.as_view(), name='news_articles'),
   path('<int:pk>', NewsDetail.as_view()),
   path('create/', PostCreate.as_view(), name='news_create'),
   path('articles/create/', PostCreate.as_view(), name='articles_create'),
   path('<int:pk>/edit/', PostEdit.as_view(), name='news_edit'),
   path('<int:pk>/articles/edit/', PostEdit.as_view(), name='articles_edit'),
   path('<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
   path('<int:pk>/articles/delete/', PostDelete.as_view(), name='articles_delete')
]