from django.shortcuts import render, redirect
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from annoying.functions import get_object_or_None

from django.http import HttpResponse

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from .models import MenuItem, Category, OrderModel

from rest_framework.decorators import api_view
from .helpers import send_otp_to_phone

# Create your views here.
@login_required(login_url='login_view')
def index(request):
    return render(request, 'rishabs/shop.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if User.objects.get(phone_number=username).is_staff:
                    orders = OrderModel.objects.all()
                    total_revenue = 0
                    for order in orders:
                        total_revenue += order.price

                    context = {
                        'orders':orders,
                        'total_revenue':total_revenue,
                        'total_orders':len(orders),
                    }
                    login(request, user)
                    return render(request, 'restaurent/dashboard.html',context)
            elif User.objects.get(phone_number=username).is_phone_verified:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, 'rishabs/login.html', {'message': 'Invalid Credentials'})

    return render(request, 'rishabs/login.html')



def register_view(request):

    if request.method == "POST":
        name = request.POST["username"]
        password = request.POST["password"]
        password2 = request.POST["cpassword"]
        phone_number = request.POST["phone_number"]
        email = request.POST["email"]

        if password == password2 and password!=None:

            user = User.objects.create_user(
                username = name,
                password = password,
                phone_number = phone_number,
                otp = send_otp_to_phone(phone_number),
                email = email
            )
            user.set_password = password
            user.save()

            return render(request, 'rishabs/verify.html')

        else:
            return render(request, 'rishabs/register.html', {'message': 'Passwords do not match'})


    return render(request, 'rishabs/register.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login_view"))

@api_view(['POST'])
def verify(request):
    if request.method == "POST":
        phone_number = request.POST["phone_number"]
        otp1 = request.POST["otp1"]

        try:
            user_obj = User.objects.get(phone_number = phone_number)

        except Exception as e:
            return render(request, 'rishabs/verify.html', {'message': 'Phone Number does not Exists'})
    
        if user_obj.otp == otp1:
            user_obj.is_phone_verified = True
            user_obj.save()
            return render(request, 'rishabs/login.html')

        return render(request, 'rishabs/verify.html', {'message': 'Phone Number does not Exists'})

    else:
        return render(request, 'rishabs/verify.html')

def order(request):
    if request.method == "POST":

        order_items = {
            'items': []
        }

        items = request.POST.getlist('items[]')
        if items == []:
            juice = MenuItem.objects.filter(category__name__contains='juice')
            hot_drinks = MenuItem.objects.filter(category__name__contains='hot_drinks')
            snacks = MenuItem.objects.filter(category__name__contains='snacks')

            # pass into context
            context = {
                'juice': juice,
                'hot_drinks': hot_drinks,
                'snacks': snacks,
                'error': "Please select atleast one item!",
            }

            # render the template
            return render(request, 'rishabs/order.html', context)
        else:
            for item in items:
                #print(item)
                menu_item = get_object_or_None(MenuItem, id=int(item))
                #print(menu_item)
                #menu_item = MenuItem.objects.get(pk__contains=int(item))
                item_data = {
                    'id': menu_item.pk,
                    'name': menu_item.name,
                    'price': menu_item.price,    
                }

                order_items['items'].append(item_data)

            price = 0
            item_ids = []

            for item in order_items['items']:
                price += item['price']
                item_ids.append(item['id'])

            order = OrderModel.objects.create(price=price,order_user=request.user)
            #order.order_user.add(request.user)
            order.items.add(*item_ids)

            # context = {
            #     'items': order_items['items'],
            #     'price': price,
            #     'username' : request.user.username
            # }
            context = {
                'order':order
            }
            
            return render(request, 'rishabs/customer_order_details.html', context)

    if request.method == "GET":

        juice = MenuItem.objects.filter(category__name__contains='juice')
        hot_drinks = MenuItem.objects.filter(category__name__contains='hot_drinks')
        snacks = MenuItem.objects.filter(category__name__contains='snacks')

        # pass into context
        context = {
            'juice': juice,
            'hot_drinks': hot_drinks,
            'snacks': snacks,
        }

        # render the template
        return render(request, 'rishabs/order.html', context)


def profile_view(request):
    return render(request, 'rishabs/profile.html')

def rorder_details(request,pk):
    if request.method == "POST":
        order = OrderModel.objects.get(pk=pk)
        order.delete()

        juice = MenuItem.objects.filter(category__name__contains='juice')
        hot_drinks = MenuItem.objects.filter(category__name__contains='hot_drinks')
        snacks = MenuItem.objects.filter(category__name__contains='snacks')

        # pass into context
        context = {
            'juice': juice,
            'hot_drinks': hot_drinks,
            'snacks': snacks,
            'message':'Order has been cancelled!'
        }

        # render the template
        return render(request, 'rishabs/order.html', context)

    else:
        check = OrderModel.objects.filter(pk=pk)
        
        if len(check)>0:
            order = OrderModel.objects.get(pk=pk)
        else:
            juice = MenuItem.objects.filter(category__name__contains='juice')
            hot_drinks = MenuItem.objects.filter(category__name__contains='hot_drinks')
            snacks = MenuItem.objects.filter(category__name__contains='snacks')

            # pass into context
            context = {
                'juice': juice,
                'hot_drinks': hot_drinks,
                'snacks': snacks,
                'message' : 'Order has been cancelled!',
            }

            # render the template
            return render(request, 'rishabs/order.html', context)

        context = {
            'order':order
        }
        return render(request, 'rishabs/rorder_details.html',context)


def feedback(request):
    if request.method == "POST":

        feedback_text = request.POST.getlist('comment[]')
        orders = OrderModel.objects.all()
        #feedback_text = request.GET('comment')
        #order = OrderModel.objects.filter(order_user=request.user)
        order = OrderModel.objects.filter(order_user=request.user)
        order1 = order[len(order)-1]
        order1.feedback = feedback_text
        order1.save()


        juice = MenuItem.objects.filter(category__name__contains='juice')
        hot_drinks = MenuItem.objects.filter(category__name__contains='hot_drinks')
        snacks = MenuItem.objects.filter(category__name__contains='snacks')

        # pass into context
        context = {
            'juice': juice,
            'hot_drinks': hot_drinks,
            'snacks': snacks,
            'fed':'Thanks for the Feedback',
        }

        # render the template
        return render(request, 'rishabs/order.html', context)
    else:
        return render(request, 'rishabs/feedback.html')
