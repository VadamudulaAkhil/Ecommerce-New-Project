import json
from . models import *

def cartCookies(request):

    try:
            cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print('Cart:',cart)
    items = []
    order = {'get_cart_total':0, 'get_cart':0, 'shipping':False}
    cartItems = order['get_cart']

    for i in cart:
        try:

            cartItems += cart[i]['quantity']
            
            product = Product.objects.get(id = i)
            total = product.price * cart[i]['quantity']

            order['get_cart_total'] += total
            order['get_cart'] += cart[i]['quantity']

            item = {
                'product' : {
                    'id' : product.id,
                    'name' : product.name,
                    'price' : product.price,
                    'imageURL' : product.imageURL
                },
                'quantity' : cart[i]['quantity'],
                'get_total' : total
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True

        except:
            pass
    return {'items':items, 'order':order, 'cartItems':cartItems}

def cartData(request):
     
    if request.user.is_authenticated:
        customer = request.user.customer
        order, create = Order.objects.get_or_create(customer = customer, complete = False, defaults={'date_ordered':timezone.now()})
        items = order.orderitem_set.all()
        cartItems = order.get_cart
    else:
        CookieData = cartCookies(request)
        items = CookieData['items']
        order = CookieData['order']
        cartItems = CookieData['cartItems']

    return {'items':items, 'order':order, 'cartItems':cartItems}