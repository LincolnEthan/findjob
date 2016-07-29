# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.conf import settings
from .models import Blog,Tag
from main.libs.tag_cloud import TagCloud
class BlogListView(ListView):
    template_name="blog/post_list.html"
    paginate_by = settings.PAGE_SIZE
    context_object_name="blog_list"
    def get_queryset(self):
        query_condition = {
        'status': 'p',
        'is_public': True
    }

        if 'tag_name' in self.kwargs:
            query_condition['tags__title'] = self.kwargs['tag_name']
        elif 'cat_name' in self.kwargs:
            query_condition['category__title'] = self.kwargs['cat_name']

        return Blog.objects.filter(**query_condition).order_by('-publish_time')

class BlogDetailView(DetailView):
    model = Blog
    template_name = "blog/post_detail.html"
    def get_object(self, queryset=None):
        blog = super(BlogDetailView, self).get_object(queryset)
        if blog.link != self.kwargs['blog_link']:
            raise Http404()
    
        if blog.status == 'd' or (not blog.is_public and self.request.user != blog.author):
            raise PermissionDenied
        # 阅读数增1
        blog.access_count += 1
        blog.save(modified=False)
        return blog    

class BlogListByCategoryView(ListView):
    template_name = 'blog/post_list.html'
    paginate_by = settings.PAGE_SIZE
    context_object_name = "blog_list"

    def get_queryset(self):
        # 只显示状态为发布且公开的文章列表
        query_condition = dict({'status': 'p', 'is_public': True})
        query_condition['category__id'] = self.kwargs['pk']
        return Blog.objects.filter(**query_condition).order_by('-publish_time')

class ArchiveView(ListView):
    template_name = "blog/archive_blog.html"
    context_object_name = "blog_list"
    paginate_by = settings.PAGE_SIZE*2

    def get_queryset(self):
        return Blog.objects.filter(status='p').order_by('-publish_time')
    
class TagListView(ListView):
    template_name = 'blog/tag_list.html'
    context_object_name = 'tag_list'
    model = Tag

    def get_context_data(self, **kwargs):
        context = super(TagListView, self).get_context_data(**kwargs)
        tag_list = context.get("tag_list")
        # 有博文的tag
        tag_list_have_blog = []
        for tag in tag_list:
            blog_count = Blog.objects.filter(tags__pk=tag.id).count()
            if blog_count > 0:
                tag.blog_count = blog_count
                tag_list_have_blog.append(tag)

        max_count = min_count = 0
        if len(tag_list_have_blog) > 0:
            max_count = max(tag_list_have_blog, key=lambda tag: tag.blog_count).blog_count
            min_count = min(tag_list_have_blog, key=lambda tag: tag.blog_count).blog_count

        tag_cloud = TagCloud(min_count, max_count)

        for tag in tag_list_have_blog:
            tag_font_size = tag_cloud.get_tag_font_size(tag.blog_count)
            color = tag_cloud.get_tag_color(tag.blog_count)
            tag.color = color
            tag.font_size = tag_font_size

        context['tag_list'] = tag_list_have_blog
        context['tag_active'] = True
        return context
    
    

