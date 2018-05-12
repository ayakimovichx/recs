from django.shortcuts import get_object_or_404, render

from .models import View, Product

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