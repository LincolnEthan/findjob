# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from django.db import models
from django.contrib.auth.models import User
class Book(models.Model):
    STATUS_CHOICES = (
        ('d', "草稿"),
        ('p', "已发布"),
    )    
    title=models.CharField(max_length=250)
    slug=models.SlugField()
    thumbnail=models.ImageField(upload_to="books/thumbnails")
                                
    file = models.FileField(upload_to='books/files')
    
    add_time = models.DateTimeField('创建时间', auto_now_add=True)
    publish_time = models.DateTimeField('发表时间', null=True)
    update_time = models.DateTimeField('修改时间')
    
    status = models.CharField('状态', max_length=1, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])    
    
    category = models.ForeignKey('Category', verbose_name='所属分类')
    owner = models.ForeignKey(User,verbose_name='所属者')
    tags = models.ManyToManyField('Tag', verbose_name='标签集合', null=True, blank=True)
    class Meta:
        ordering = ['update_time', ]
        verbose_name = '书籍'
        verbose_name_plural = '书籍'
    
    def __unicode__(self):
        return self.title
    

class Category(models.Model):
    """
    大分类
    """
    title = models.CharField('名称', max_length=50, db_index=True, unique=True)

    class Meta:
        ordering = ['title', ]
        verbose_name = '书籍分类'
        verbose_name_plural = '书籍分类'

    def __str__(self):
        return self.title


class Tag(models.Model):
    """
    小标签
    """
    title = models.CharField('名称', max_length=50, db_index=True, unique=True)

    def save(self, *args, **kwargs):
        self.title = re.sub("\s", "", self.title)
        super(Tag, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'

    def __str__(self):
        return self.title

    
    
    
