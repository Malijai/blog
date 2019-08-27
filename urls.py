from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import index, BlogDetail, listing


urlpatterns = [
#    url(r'^$', BlogIndex.as_view(), name='blogindex'),
    path('', listing, name='blogindex'),
    path('index/', index),
    path('recherche/', views.get_recherchetexte, name='recherche'),
    path('<int:pk>',login_required(BlogDetail.as_view()), name='blogdetail'),
    path('<int:pk>/comment/new/', views.commentaire_new, name='commentaire_new'),
    path('tag/<slug:slug>.html', views.view_tag, name='view_blog_tag'),
    path('entree/new/', views.entree_new, name='entree_new'),
    path('tag/new/', views.tag_new, name='tag_new'),
]
