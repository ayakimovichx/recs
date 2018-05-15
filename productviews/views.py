from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from .models import View, Product
from .suggestions import update_recs, run_user_recs

def view_list(request):
    latest_view_list = View.objects.order_by('-pub_date')[:9]
    context = {'latest_view_list':latest_view_list}
    return render(request, 'productviews/view_list.html', context)


def product_list(request):
    product_list = Product.objects.order_by('-name')
    context = {'product_list':product_list}
    return render(request, 'productviews/product_list.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'productviews/product_detail.html', {'product': product})
    
def user_view_list(request, username=None):
    if not username:
        username = request.user.username
    latest_view_list = View.objects.filter(user_name=username).order_by('-pub_date')
    context = {'latest_view_list':latest_view_list, 'username':username}
    return render(request, 'productviews/user_view_list.html', context)
    
@login_required
def user_recommendation_list(request, username=None):
    if not username:
        username = request.user.username
    # get this user views
    user_views = View.objects.filter(user_name=username).prefetch_related('product')
    # from the views, get a set of product IDs
    user_views_product_ids = set(map(lambda x: x.product.id, user_views))
    
    try:
        user_name_current = \
            User.objects.get(username=request.user.username).id
        run_user_recs()
    except: # if no user
        update_recs()
        user_name_current = \
            User.objects.get(username=request.user.username).id
    
    # then get a product list excluding the previous IDs
    product_list = Product.objects.exclude(id__in=user_views_product_ids)

    return render(
        request, 
        'productviews/user_recommendation_list.html', 
        {'username': username,'product_list': product_list}
    )

