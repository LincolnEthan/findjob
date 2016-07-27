from django.conf.urls import url
from . import views 
urlpatterns=[
    url(r"^tags$", views.TagListView.as_view(), name="tag_list"),
    url(r"^tag/(?P<tag_id>[\w,-]+)$", views.BookListView.as_view(), name="tag"),
    url(r"^category/(?P<pk>\d+)/(?P<cat_name>\w+)$", views.BookListByCategoryView.as_view(), name="category"),
   url(r'^$',views.BookListView.as_view(),name='index'),
]
