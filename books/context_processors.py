# -*- coding: utf-8 -*-
from .models import Book,Category

def recent_book_list(request):
    """
    最近文章列表
    """
    # 最近发布的文章列表
    recent_books = Book.objects.filter(status='p').order_by('-publish_time')[:4]

    # 分类
    book_categories = Category.objects.all()

  

    return {'recent_books': recent_books, 'book_categories': book_categories}
