from django.contrib import admin

from .models import Book,Tag,Category

class BookAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Book,BookAdmin)
admin.site.register(Tag)
admin.site.register(Category)

