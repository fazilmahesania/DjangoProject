import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.urls.base import reverse

from .forms import OrderForm, InterestForm, RegisterForm, UpdateUserForm, UpdateProfileForm
from .models import Category, Product, Client, Order
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

# from datetime import datetime
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse


# Create your views here.

def index(request):
    cat_list = Category.objects.all().order_by('id')[:10]
    print(str(request.session.keys()))
    return render(request, 'myapp/index.html', {'cat_list': cat_list})


def about(request):
    cookie = request.COOKIES.get('about_visits')
    response = render(request, 'myapp/about.html')
    if cookie:
        cookie = int(cookie) + 1
        response.set_cookie('about_visits', str(cookie), expires=300)
    else:
        response.set_cookie('about_visits', str(1), expires=300)

    return response


def detail(request, cat_no):
    category = get_object_or_404(Category, id=cat_no)
    warehouse_location = category.warehouse
    prod_list = Product.objects.filter(category=category)
    return render(request, 'myapp/detail.html',
                  {'prod_list': prod_list, 'warehouse_loc': warehouse_location, 'cat': category})


def products(request):
    prodlist = Product.objects.all().order_by('id')[:10]
    return render(request, 'myapp/products.html', {'prodlist': prodlist})


def place_order(request):
    msg = ''
    prodlist = Product.objects.all()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['product']
            order = form.save(commit=False)
            if order.num_units <= order.product.stock:
                order.save()
                product = Product.objects.get(name=name)
                product.stock = product.stock - order.num_units
                product.save()
                msg = 'Your order has been placed successfully!!'
            else:
                msg = 'We do not have sufficient stock to fill your order!!'
            return render(request, 'myapp/order_response.html', {'msg': msg})
    else:
        form = OrderForm()
    return render(request, 'myapp/placeorder.html', {'form': form, 'msg': msg, 'prodlist': prodlist})


def productdetail(request, prod_id):
    try:
        msg = ''
        product = Product.objects.get(id=prod_id)
        if request.method == 'GET':
            form = InterestForm()
        elif request.method == 'POST':
            form = InterestForm(request.POST)
            if form.is_valid():
                interested = form.cleaned_data['interested']
                if int(interested) == 1:
                    product.interested += 1
                    product.save()
                    return redirect(reverse('myapp:index'))
        return render(request, 'myapp/productdetail.html', {'form': form, 'msg': msg, 'product': product})
    except Product.DoesNotExist:
        msg = 'The requested product does not exist. Please provide correct product id.'
        return render(request, 'myapp/productdetail.html', {'msg': msg})


# Create your views here.
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            current_dateTime = datetime.datetime.now()
            request.session['last_login'] = str(current_dateTime)
            request.session.set_expiry(3600)
            print(request.session.keys(), request.session.values())
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('myapp:myorders'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            return HttpResponse('Invalid login details.')
    else:
        return render(request, 'myapp/login.html')


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'myapp/password_reset.html'
    email_template_name = 'myapp/password_reset_email.html'
    subject_template_name = 'myapp/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('myapp:login')

@login_required(login_url='/myapp/login/')
def myorders(request):
    user = request.user
    clients = list(Client.objects.values_list('username', flat=True))
    if str(user) in clients:
        id = Client.objects.values_list('id', flat=True).filter(username=str(user))[0]
        orders = list(Order.objects.values().filter(client_id=id))
        for order in orders:
            order['name']=Product.objects.values('name').filter(id=order['product_id'])[0]['name']
        return render(request, 'myapp/myorders.html', {'orderlist': orders, 'isClient': True})
    else:
        return render(request, 'myapp/myorders.html', {'orderlist': [], 'isClient': False})
        # return render(request, 'myapp/login.html')
        # return user_login(request)


@login_required
def user_logout(request):
    logout(request)
    # return HttpResponseRedirect(reverse(('myapp:index')))
    return render(request, 'myapp/login.html')


def user_register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect("myapp:login")
        else:
            print('form invalid')
    else:
        form = RegisterForm()
    return render(request=request, template_name="myapp/register.html", context={"register_form": form})


@login_required
def profile(request):
    print(request.method)
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        print(profile_form)
        print(request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # messages.success(request, 'Your profile is updated successfully')
            return redirect('myapp:users-profile')
        else:
            print("invalid")
    else:
        user_form = UpdateUserForm(instance=request.user)
        # user_form.save()
        # print(request.user.profile)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'myapp/profile.html', {'user_form': user_form, 'profile_form': profile_form})


