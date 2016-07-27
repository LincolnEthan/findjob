# -*- coding: utf-8 -*-
from django.shortcuts import render
from .models import Book
from django.conf import settings
from django.views.generic.list import ListView
from main.libs.tag_cloud import TagCloud
from .models import Tag
def index(request):
    object_list=Book.objects.all()
    return render(request,'books/index.html',{'object_list':object_list})


class BookListView(ListView):
    template_name="books/index.html"
    paginate_by = settings.PAGE_SIZE
    context_object_name="book_list"
    def get_queryset(self):
        query_condition = {
        'status': 'p',
        }

        if 'tag_id' in self.kwargs:
            query_condition['tags__id'] = self.kwargs['tag_id']
        elif 'cat_name' in self.kwargs:
            query_condition['category__title'] = self.kwargs['cat_name']
            
        return Book.objects.filter(**query_condition).order_by('-publish_time')

class TagListView(ListView):
    template_name = 'books/tag_list.html'
    context_object_name = 'tag_list'
    model = Tag

    def get_context_data(self, **kwargs):
        context = super(TagListView, self).get_context_data(**kwargs)
        tag_list = context.get("tag_list")
        # 有博文的tag
        tag_list_have_book = []
        for tag in tag_list:
            book_count = Book.objects.filter(tags__pk=tag.id).count()
            if book_count > 0:
                tag.book_count = book_count
                tag_list_have_book.append(tag)

        max_count = min_count = 0
        if len(tag_list_have_book) > 0:
            max_count = max(tag_list_have_book, key=lambda tag: tag.book_count).book_count
            min_count = min(tag_list_have_book, key=lambda tag: tag.book_count).book_count

        tag_cloud = TagCloud(min_count, max_count)

        for tag in tag_list_have_book:
            tag_font_size = tag_cloud.get_tag_font_size(tag.book_count)
            color = tag_cloud.get_tag_color(tag.book_count)
            tag.color = color
            tag.font_size = tag_font_size

        context['tag_list'] = tag_list_have_book
        context['tag_active'] = True
        return context

class BookListByCategoryView(ListView):
    template_name = 'books/index.html'
    paginate_by = settings.PAGE_SIZE
    context_object_name = "book_list"

    def get_queryset(self):
        # 只显示状态为发布且公开的文章列表
        query_condition = dict({'status': 'p'})
        query_condition['category__id'] = self.kwargs['pk']
        return Book.objects.filter(**query_condition).order_by('-publish_time')