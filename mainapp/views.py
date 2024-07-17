from django.shortcuts import render,HttpResponseRedirect,redirect
from .models import*
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from random import randint
from django.conf import settings
from django.core.mail import send_mail
import razorpay
from supershop.settings import RAZORPAY_API_KEY ,RAZORPAY_API_SECRET_KEY
# Create your views here.

def homepage(Request):
    products=Product.objects.all().order_by("-id")[0:12]
    testimonial=Testimonial.objects.all().order_by("-id")
    return render(Request,'index.html',{'products':products,'testimonial':testimonial})

def aboutpage(Request):
    testimonial=Testimonial.objects.all().order_by("-id")
    return render(Request,'about.html',{'testimonial':testimonial})

def addTOCartPage(request):
    if request.method == "POST":
        cart = request.session.get('cart', None)
        qty = request.POST.get("qty")
        id = request.POST.get("id")

        print("POST data:", request.POST)
        print("Received POST data - qty:", qty, "id:", id)

        try:
            # Validate and convert id and qty to integers
            if not id or not qty:
                raise ValueError("Missing id or qty")

            id = int(id)
            qty = int(qty)

            # Fetch the product
            p = Product.objects.get(id=id)

            # Initialize or update the cart
            if cart:
                if str(id) in cart.keys():
                    item = cart[str(id)]
                    item['qty'] += qty
                    item['total'] += qty * item['price']
                    cart[str(id)] = item
                else:
                    cart[str(id)] = {
                        'product_id': id,
                        'name': p.name,
                        'brand': p.brand.name,  # Convert Brand to a serializable format
                        'color': p.color,
                        'size': p.size,
                        'price': p.finalprice,
                        'qty': qty,
                        'total': qty * p.finalprice,
                        'pic': p.pic1.url
                    }
            else:
                cart = {
                    str(id): {
                        'product_id': id,
                        'name': p.name,
                        'brand': p.brand.name,  # Convert Brand to a serializable format
                        'color': p.color,
                        'size': p.size,
                        'price': p.finalprice,
                        'qty': qty,
                        'total': qty * p.finalprice,
                        'pic': p.pic1.url
                    }
                }

            # Save the cart in session
            request.session['cart'] = cart
            request.session.set_expiry(60 * 60 * 24 * 30)  # Session expiry set to 30 months
            print("Session set:", request.session['cart'])  # Debug print

        except ValueError as e:
            print("Invalid id or qty value:", e)  # Log if id or qty is not valid
        except Product.DoesNotExist:
            print("Product with id", id, "does not exist")  # Log if the product does not exist
        except Exception as e:
            print("Error:", e)  # Log other exceptions

    return HttpResponseRedirect("/cart/")

def cartpage(request):
    cart = request.session.get('cart', None)
    subtotal=0
    shipping=0
    total =0
    if(cart):
        for value in cart.values():
            subtotal=subtotal + value['total']
        if(subtotal>0 and subtotal<4000):
            shipping = 150
        total =subtotal + shipping
    return render(request, 'cart.html', {'cart': cart,'subtotal':subtotal,'shipping':shipping,'total':total})

def deleteCart(Request,id):
    cart = Request.session.get('cart',None)
    if(cart):
        del cart[str(id)]
        Request.session['cart']=cart
    else:
        pass
    return HttpResponseRedirect("/cart")

def updateCart(Request,id,op):
    cart = Request.session.get('cart',None)
    if(cart):
        item = cart[id]
        if(op=='dec' and item['qty']==1):
            return HttpResponseRedirect("/cart")
        
        else:
            if(op=='dec'):
                item['qty'] = item['qty']-1
                item['total'] = item['total']-item['price']
            else:
                item['qty'] = item['qty']+1
                item['total'] = item['total']+item['price']
        cart[id]=item
        Request.session['cart']=cart
    else:
        pass 
    return HttpResponseRedirect("/cart")

client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))

@login_required(login_url="/login/")
def checkoutpage(request):
    try:
        buyer = Buyer.objects.get(username=request.user.username)
        cart = request.session.get('cart', {})
        subtotal = sum(item['total'] for item in cart.values())
        shipping = 150 if 0 < subtotal < 4000 else 0
        total = subtotal + shipping

        if request.method == 'POST':
            mode = request.POST.get("mode")
            payment_mode = 0 if mode == 'COD' else 1 if mode == 'NetBanking' else None

            if payment_mode is None:
                raise ValueError("Invalid payment mode selected")

            checkout = Checkout(
                buyer=buyer,
                subtotal=subtotal,
                total=total,
                shipping=shipping,
                paymentmode=payment_mode
            )
            checkout.save()

            for key, value in cart.items():
                p = Product.objects.get(id=int(key))
                cp = CheckoutProduct(
                    checkout=checkout,
                    product=p,
                    qty=value['qty'],
                    total=value['total']
                )
                cp.save()
            request.session['cart'] = {}

            if mode == "COD":
                return HttpResponseRedirect("/confirmation/")
            else:
                order_amount = checkout.total * 100  # Convert to paise
                order_currency = "INR"
                payment_order = client.order.create(dict(amount=order_amount, currency=order_currency))
                payment_id = payment_order['id']
                checkout.paymentmode = 1
                checkout.save()
                return render(request, "pay.html", {
                    "amount": order_amount,
                    "api_key": settings.RAZORPAY_API_KEY,
                    "order_id": payment_id,
                    "User": buyer,
                    "id":checkout.id
                })
        return render(request, 'checkout.html', {'buyer': buyer, 'total': total, 'shipping': shipping, 'subtotal': subtotal, 'cart': cart})
    except Exception as e:
        print(f"An error occurred: {e}")
        return HttpResponseRedirect("/admin/")

@login_required(login_url="/login/")
def rePayment(request, id):
    try:
        buyer = Buyer.objects.get(username=request.user.username)
        checkout = Checkout.objects.get(id=id)
        order_amount = checkout.total * 100  # Convert to paise
        order_currency = "INR"
        payment_order = client.order.create(dict(amount=order_amount, currency=order_currency))
        payment_id = payment_order['id']
        checkout.paymentmode = 1
        checkout.save()
        return render(request, "pay.html", {
            "amount": order_amount,
            "api_key": settings.RAZORPAY_API_KEY,
            "order_id": payment_id,
            "User": buyer,
            "id":id
        })
    except Exception as e:
        print(f"An error occurred: {e}")
        return HttpResponseRedirect('/profile/')


@login_required(login_url="/login/")
def paymentSuccess(request,id, rpid, rpoid, rpsid):
    checkouts = Checkout.objects.get(id=id)
    if checkouts.exists():
        checkout = checkouts.first()
        checkout.rpid = rpid
        checkout.paymentstatus = 1
        checkout.save()
    return HttpResponseRedirect('/confirmation/'+id+'/')


@login_required(login_url="/login/")
def confirmationpage(request,id):
    try:
        buyer = Buyer.objects.get(username=request.user.username)

        cart = CheckoutProduct.objects.filter(checkout=Checkout.objects.get(id=id))
        subtotal = 0
        shipping = 0
        total = 0

        if cart:
            for item in cart:
                subtotal += item.total
            if 0 < subtotal < 4000:
                shipping = 150
            total = subtotal + shipping

        request.session['cart'] = {}
        return render(request, 'confirmation.html', {'cart': cart, 'subtotal': subtotal, 'shipping': shipping, 'total': total, 'buyer': buyer, 'checkout': checkout})
    except Exception as e:
        print(f"An error occurred: {e}")
        return HttpResponseRedirect("/admin/")
    
def contactpage(Request):
    if(Request.method=="POST"):
        c=Contact()
        c.name = Request.POST.get("name")
        c.email = Request.POST.get("email")
        c.phone = Request.POST.get("phone")
        c.subject = Request.POST.get("subject")
        c.message = Request.POST.get("message")
        c.save()
        messages.success(Request,"Thanks To share your query with us!!! ")
    return render(Request,'contact.html')

# def shoppage(Request,mc,sc,br):
#     if(mc=="All" and sc=="All" and br=="All"):
#         products= Product.objects.all().order_by("-id")
        
#     elif(mc!="All" and sc=="All" and br=="All"):
#         products= Product.objects.filter(maincategory=MainCategory.objects.get(name=mc)).order_by("-id")
    
#     elif(mc=="All" and sc!="All" and br=="All"):
#         products= Product.objects.filter(subcategory=SubCategory.objects.get(name=sc)).order_by("-id")
    
#     elif(mc!="All" and sc=="All" and br!="All"):
#         products= Product.objects.filter(brand=Brand.objects.get(name=br)).order_by("-id")
    
    
#     mainCategory=MainCategory.objects.all().order_by("-id")
#     subCategory=SubCategory.objects.all().order_by("-id")
#     brand=Brand.objects.all().order_by("-id")
#     return render(Request,'shop.html',{'products':products,'maincategory':mainCategory,'subcategory':subCategory,'brand':brand,'mc':mc,'sc':sc,'br':br})

def search(Request):
    if(Request.method=="POST"):
        search=Request.POST.get("search")
        try:
            maincategory=MainCategory.objects.get(name=search)
        except:
            maincategory=None
            
        try:
            subcategory=SubCategory.objects.get(name=search)
        except:
            subcategory=None
            
        try:
            brand=Brand.objects.get(name=search)
        except:
            brand=None
            
        products=Product.objects.filter(Q(name__icontains=search)|Q(maincategory=maincategory)|Q(subcategory=subcategory)|Q(brand=brand))
        
        mainCategory = MainCategory.objects.all().order_by("-id")
        subCategory = SubCategory.objects.all().order_by("-id")
        brand = Brand.objects.all().order_by("-id")
        return render(Request, 'shop.html', {'products': products, 'maincategory': mainCategory, 'subcategory': subCategory, 'brand': brand, 'mc': "All", 'sc': "All", "br": "All"})
    else:
        return HttpResponseRedirect("/")

def shoppage(Request, mc, sc, br):
    filters = Q()
    if mc != "All":
        filters &= Q(maincategory=MainCategory.objects.get(name=mc))
    if sc != "All":
        filters &= Q(subcategory=SubCategory.objects.get(name=sc))
    if br != "All":
        filters &= Q(brand=Brand.objects.get(name=br))

    products = Product.objects.filter(filters).order_by("-id")

    mainCategory = MainCategory.objects.all().order_by("-id")
    subCategory = SubCategory.objects.all().order_by("-id")
    brand = Brand.objects.all().order_by("-id")
    
    testimonial=Testimonial.objects.all().order_by("-id")
    return render(Request, 'shop.html', {'products': products, 'maincategory': mainCategory, 'subcategory': subCategory, 'brand': brand, 'mc': mc, 'sc': sc, 'br': br,'testimonial':testimonial})

def singleproductpage(Request,id):
    products = Product.objects.get(id=id)
    context = {'products': products}
    return render(Request,'single-product.html',context)

@login_required(login_url="/login/")
def profilepage(Request):
    if(Request.user.is_superuser):
        return HttpResponseRedirect("/admin/")
    username=Request.user.username
    
    buyer=Buyer.objects.get(username=username)
    wishlist=Wishlist.objects.filter(buyer=buyer)
    checkout=Checkout.objects.filter(buyer=buyer)
    orders =[]
    for i in checkout:
        cp=CheckoutProduct.objects.filter(checkout=i)
        orders.append({'checkout':i,'cp':cp})
    # print(orders,"\n\n\n")
    return render(Request,'profile.html',{'buyer':buyer,'wishlist':wishlist,'orders':orders})
    
@login_required(login_url="/login/")
def updateProfilePage(Request):
    if(Request.user.is_superuser):
        return HttpResponseRedirect("/admin")
    username=Request.user.username
    
    buyer=Buyer.objects.get(username=username)
    if(Request.method=='POST'):
        buyer.name=Request.POST.get("name")
        buyer.email=Request.POST.get("email")
        buyer.address=Request.POST.get("address")
        buyer.city=Request.POST.get("city")
        buyer.state=Request.POST.get("state")
        buyer.pin=Request.POST.get("pin")
        if(Request.FILES.get("pic")):
            buyer.pic=Request.FILES.get("pic")
        buyer.save()
        return HttpResponseRedirect("/profile/")
    return render(Request,'updateprofile.html',{'buyer':buyer})
    
    
def loginpage(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_superuser:
                # print("Superuser logged in, redirecting to /admin")
                return HttpResponseRedirect("/admin")
            else:
                # print("User logged in, redirecting to /profile/")
                return HttpResponseRedirect("/profile/")
        else:
            messages.error(request, "Invalid Username Or Password")
            # print("Invalid login attempt")
    print("Rendering login page")
    return render(request, 'login.html')

@login_required(login_url="/login/")
def logoutPage(request):
    logout(request)
    print("User logged out, redirecting to /login/")
    return HttpResponseRedirect("/login/")

def signuppage(request):
    if request.method == 'POST':
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")
        if password == cpassword:
            username = request.POST.get("username")
            email = request.POST.get("email")
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered!")
            else:
                User.objects.create_user(username=username, email=email, password=password)
                name = request.POST.get("name")
                # phone = request.POST.get("phone")

                b = Buyer(name=name, email=email, username=username)
                b.save()

                messages.success(request, "Account created successfully! Please log in.")
                return HttpResponseRedirect("/login")
        else:
            messages.error(request, "Password and confirm password do not match!")

    return render(request, 'signup.html')

@login_required(login_url="/login/")
def wishlistpage(request, id):
    buyer = Buyer.objects.get(username=request.user.username)
    product = Product.objects.get(id=id)
    try:
        w = Wishlist.objects.get(product=product, buyer=buyer)
    except Wishlist.DoesNotExist:
        w = Wishlist(product=product, buyer=buyer)
        w.save()
    return HttpResponseRedirect("/profile")

@login_required(login_url="/login/")
def deletewishlist(request,id):
    try:
        w=Wishlist.objects.get(id=id)
        w.delete()
    except:
        pass
    return HttpResponseRedirect("/profile/")


def NewslatterSubscribe(request):
    if(request.method=="POST"):
        email=request.POST.get("email")
        n=Newslatter()
        n.email=email
        try:
            n.save()
            messages.success(request,"Thanks to Subscribe Our Newslatter Services!!!")
        except:
            messages.error(request,"Your Email is Already Subcribe!!")
        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
    
# forget password and send otp on for reset passsword 
def ForgetPassword1(request):
    if(request.method=="POST"):
        username=request.POST.get("username")
        try:
            buyer=Buyer.objects.get(username=username)
            otp=randint(100000,999999)
            buyer.otp=otp
            buyer.save()
            
            subject='OTP for Password Reset !! team-: SuperShop'
            message="""
            hello  """+buyer.name+""" 
            OTP For Password Reset Is """ + str(otp)+"""
            Please Never Share Your OTP With Anyone           
            """
            email_from= settings.EMAIL_HOST_USER
            recipient_list=[buyer.email, ]
            send_mail(subject,message,email_from,recipient_list)
            request.session['reset-password-user']=buyer.username
            return HttpResponseRedirect("/forget-password2/")
        except:
            messages.error(request,"Username Not Found! Enter Valid Username!!!")
    return render(request,'forget-password1.html')

# get otp and enter otp for reset password
def ForgetPassword2(request):
    username=request.session.get("reset-password-user")
    if(request.method=='POST'):
        otp=int(request.POST.get("otp"))
        buyer=Buyer.objects.get(username=username)
        if(otp==buyer.otp):
            
            return HttpResponseRedirect("/forget-password3/")
        else:
            messages.error(request,"Invalid OTP")
        
    if(username):
        return render(request,'forget-password2.html')
    else:
        return HttpResponseRedirect("/forget-password1/")
        

#change password
def ForgetPassword3(request):
    username=request.session.get("reset-password-user")
    if(request.method=='POST'):
        # if(username):
        password=request.POST.get("password")
        cpassword=request.POST.get("cpassword")
        if(password==cpassword):
            user=User.objects.get(username=username)
            user.set_password(password)
            user.save()
            del request.session['reset-password-user']
            messages.success(request,"Now Login Your Password is Reset")
            return HttpResponseRedirect("/login/")
        else:
            messages.error(request,"password and confirm password does not match")
        
    if(username):
        return render(request,'forget-password3.html')
    else:
        return HttpResponseRedirect("/forget-password1/")
        
        