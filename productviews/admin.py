from django.contrib import admin

from .models import Product, View

class ViewAdmin(admin.ModelAdmin):
    model = View
    list_display = ('product', 'rating', 'user_name', 'pub_date')
    list_filter = ['pub_date', 'user_name']
    search_fields = ['product']
    
admin.site.register(Product)
admin.site.register(View, ViewAdmin)