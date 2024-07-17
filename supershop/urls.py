"""
URL configuration for supershop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from mainapp import views as mainapp
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',mainapp.homepage,name='home'),
    path('about/',mainapp.aboutpage,name='about'),
    path('add-to-cart/',mainapp.addTOCartPage,name='add-to-cart'),
    path('cart/',mainapp.cartpage,name='cart'),
    path('delete-cart/<str:id>/',mainapp.deleteCart,name='delete-cart'),
    path('update-cart/<str:id>/<str:op>',mainapp.updateCart,name='update-cart'),
    path('checkout/',mainapp.checkoutpage,name='checkout'),
    path('re-payment/<int:id>/',mainapp.rePayment,name='re-payment'),
    path('payment-success/<int:id>/<str:rpid>/<str:rpoid>/<str:rpsid>/',mainapp.paymentSuccess,name='payment-success'),
    path('confirmation/<int:id>/',mainapp.confirmationpage,name='confirmation'),
    path('contact/',mainapp.contactpage,name='contact'),
    path('login/',mainapp.loginpage,name='login'),
    path('logout/',mainapp.logoutPage,name='logout'),
    path('signup/',mainapp.signuppage,name='signup'),
    path('profile/',mainapp.profilepage,name='profile'),
    path('updateprofile/',mainapp.updateProfilePage,name='updateprofile'),
    # path('shop/<str:mc>/<str:sc>/<str:br>/',mainapp.shoppage,name='shop'),
    path('shop/<str:mc>/<str:sc>/<str:br>/',mainapp.shoppage),
    path('single-product/<int:id>/',mainapp.singleproductpage,name='single-product'),
    # path('add-to-wishlist/<int:id>/',mainapp.wishlistpage,name="add-to-wishlist")
    path('add-to-wishlist/<int:id>/', mainapp.wishlistpage, name='add-to-wishlist'),
    path('delete-wishlist/<int:id>/', mainapp.deletewishlist, name='delete-wishlist'),
    path('newslatter/subscribe/', mainapp.NewslatterSubscribe, name='newslatter-subscribe'),
    path('search/', mainapp.search, name='search'),
    path('forget-password1/', mainapp.ForgetPassword1, name='forget-password1'),
    path('forget-password2/', mainapp.ForgetPassword2, name='forget-password2'),
    path('forget-password3/', mainapp.ForgetPassword3, name='forget-password3'),
    
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
