from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from django.utils import timezone
from .models import *
from . utils import cartCookies, cartData
from django.contrib.auth import authenticate, login
from django.http import Http404

import razorpay
from django.conf import settings
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# def UserDetails(request):
#     if request.user.authenticated == 'POST':
#         customer = request.user.customer
#         userData = Customer.objects.all(customer = customer)

#     return render(request, {'userData':userData, 'customer':customer})

def Search(request):

    Data = cartData(request)
    cartItems = Data['cartItems']

    if request.method == "POST":
        Searched = request.POST['Searched']
        S_Products = Product.objects.filter(name__contains = Searched)


        return render(request, 'store/Search_Bar.html', {'Searched' : Searched, 'S_Products':S_Products, 'cartItems':cartItems})
    else:
        return render(request, 'store/Search_Bar.html')


def Register_Page(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        middlename = request.POST.get('middlename')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')

        if password != confirm_password:
            return render(request, 'store/Register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'store/Register.html', {'error': 'Username already exists'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'store/Register.html', {'error': 'Email already exists'})

        # Create the User object
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=firstname,
            last_name=lastname,
            mobile_number=mobile_number
        )

        # Create the UserProfile
        Customer.objects.create(
            user=user,
            
        )

        User_Details = {
            'firstname':firstname,
            'lastname':lastname,
            'mobile_number':mobile_number,
        }

        return render(request, 'store/Login.html', {'user':User_Details}) 

    return render(request, 'store/Register.html')


def Login_Page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
    return render(request, 'store/Login.html')



def Items(request):

    Data = cartData(request)
    cartItems = Data['cartItems']

    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request,'store/Items.html',context)
def Cart(request):
        
    Data = cartData(request)
    items = Data['items']
    order = Data['order']
    cartItems = Data['cartItems']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request,"store/Cart.html",context)
def Checkout(request):

    Data = cartData(request)
    items = Data['items']
    order = Data['order']
    cartItems = Data['cartItems']


    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request,"store/Checkout.html",context)


def UpdateItem(request):
    data = json.loads(request.body)
    ProductId = data['ProductId']
    Action = data['Action']

    print('Action:', Action)
    print('ProductId:', ProductId)

    customer = request.user.customer
    product = Product.objects.get(id = ProductId)
    order, created = Order.objects.get_or_create(customer = customer, complete = False)
    orderitem, created = OrderItem.objects.get_or_create(order = order, product = product)

    if Action == 'add' :
        orderitem.quantity = (orderitem.quantity + 1)
    elif Action == 'remove' :
        orderitem.quantity = (orderitem.quantity -1)

    orderitem.save()

    if orderitem.quantity <= 0 :
        orderitem.delete()

    items = order.orderitem_set.all()
    cart_data = {
        'cartItems': order.get_cart,
        'cartTotal': order.get_cart_total,
        'items': [
            {
                'product_id': item.product.id,
                'name': item.product.name,
                'quantity': item.quantity,
                'price': item.product.price,
                'total': item.get_total,
                'imageURL': item.product.imageURL,
            }
            for item in items
        ]
    }

    return JsonResponse(cart_data, safe=False)

def ProcessOrder(request):
    transcation_Id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order,create = Order.objects.get_or_create(customer = customer, complete = False)

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                pincode = data['shipping']['Pincode'],

            )
        

    else:
        print('User Logged out...')

        print('COOKIES:', request.COOKIES)

        name = data['form']['name']
        email = data['form']['email']

        cookieData = cartCookies(request)
        items = cookieData['items']

        customer, created = Customer.objects.get_or_create(email = email)
        customer.name = name
        customer.save()

        order = Order.objects.create(customer = customer, complete = True)

        for item in items:
            product = Product.objects.get(id = item['product']['id'])
            orderItem = OrderItem.objects.create(product = product, order = order,quantity = item['quantity'])

    total = float(data['form']['total'])
    order.transcation_id = transcation_Id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer = customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            pincode = data['shipping']['Pincode'],
            )
        
    return JsonResponse('Payment Completed', safe=False)


def CheckoutView(request):
    Data = cartData(request)
    items = Data['items']
    order = Data['order']
    product = Product.objects.all()
    return render(request, 'store/payment_check.html', {'product':product, 'items':items, 'order':order})

@method_decorator(csrf_exempt, name='dispatch')
def CreatePaymentView(request, product_id):
    product = Product.objects.get(id=product_id)
    order = Order.objects.get()

    order_data = {
        'amount': int(order.get_cart_total * 100),
        'currency': 'INR',
        'payment_capture': '1',
    }
    razorpay_order = client.order.create(order_data)


    Payment_Order.objects.create(
        user=request.user,
        product=product,
        amount=product.price,
        razorpay_order_id=razorpay_order['id']
    )

    return JsonResponse({
        'order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'product_name': product.name,
        'amount': order_data['amount'],
        'razorpay_callback_url' : settings.RAZORPAY_CALLBACK_URL
    })


def PaymentCallback(request):
    if 'razorpay_signature' in request.POST:
        order_id = request.POST.get('razorpay_order_id')
        payment_id = request.POST.get('razorpay_payment_id')
        signature = request.POST.get('razorpay_signature')

        order = Payment_Order.objects.get(razorpay_order_id = order_id)

        if client.utility.verify_payment_signature({
            'razorpay_order_id' : order_id,
            'razorpay_payment_id' : payment_id,
            'razorpay_signature' : signature,
        }):
            order.razorpay_payment_id = payment_id
            order.razorpay_signature = signature
            order.Paid = True
            order.save()
            return JsonResponse({'status' : "Success"})
        else:
            order.Paid = False
            order.save()
            return JsonResponse({'status' : "Failed"})
    else:
        return JsonResponse({'status' : 'Failed'})
    
def Feedback(request):
    
    return render(request, 'store/FeedBack.html')