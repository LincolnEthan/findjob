# -*- coding: utf-8 -*-
from .models import Blog,Category

def recent_blog_list(request):
    """
    最近文章列表
    """
    # 最近发布的文章列表
    recent_blogs = Blog.objects.filter(status='p', is_public=True).order_by('-publish_time')[:4]

    # 分类
    categories = Category.objects.all()

  

    return {'recent_blogs': recent_blogs, 'categories': categories}
