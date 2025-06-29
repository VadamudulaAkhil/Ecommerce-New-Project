from django.urls import path
from Store import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('Cart/', views.Cart, name='Cart'),
    path('Checkout/', views.Checkout, name='Checkout'),
    path('update_item/', views.UpdateItem, name='update_item'),
    path('process_order/', views.ProcessOrder, name='process_order'),
    path('register/', views.Register_Page, name='register'),
    path('', views.Items, name='store'),
    path('Search/', views.Search, name='Search'),
    path('Login/', views.Login_Page, name='Login'),
    path('Logout/', LogoutView.as_view(next_page = 'Login'), name = 'Logout'),
    # path('checkout/', views.checkout, name='checkout'),
    # path('payment-success/', views.payment_success, name='payment_success'),
    path('checkoutview/<int:product_id/', views.CheckoutView, name = 'checkoutview'),
    path('create-payment/<int:product_id/', views.CreatePaymentView, name = 'create-payment'),
    path('payment_verify', views.PaymentCallback, name='payment_verify'),
    # path('feedback/', views.Feedback, name='feedback')
    path('feedback/', views.feedback_view, name='feedback'),
    path('success/', views.success, name='success')


] 

 