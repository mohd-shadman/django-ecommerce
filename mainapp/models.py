from django.db import models
from django.core.validators import RegexValidator
# Create your models here.

class MainCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=40,unique=True)
    
    def __str__(self):
        return str(self.id)+" / "+self.name
    
    
class SubCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=40,unique=True)
    
    def __str__(self):
        return str(self.id)+" / "+self.name

  
class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=40,unique=True)
    pic =models.ImageField(upload_to="uploads/brand")
    
    def __str__(self):
        return str(self.id)+" / "+self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=40,unique=True)
    
    maincategory=models.ForeignKey(MainCategory,on_delete=models.CASCADE)
    subcategory=models.ForeignKey(SubCategory,on_delete=models.CASCADE)
    brand=models.ForeignKey(Brand,on_delete=models.CASCADE)
    
    baseprice=models.IntegerField()   
    discount=models.IntegerField()   
    finalprice=models.IntegerField()   
    stock=models.BooleanField(default=True)
    color=models.CharField(max_length=30)
    size=models.CharField(max_length=30)
    description=models.TextField(default="")
    
    pic1 =models.ImageField(upload_to="uploads/product")
    pic2 =models.ImageField(upload_to="uploads/product",default=None,blank=True,null=True)
    pic3 =models.ImageField(upload_to="uploads/product",default=None,blank=True,null=True)
    pic4 =models.ImageField(upload_to="uploads/product",default=None,blank=True,null=True)
    
    def __str__(self):
        return str(self.id)+" / "+self.name
    
class Buyer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=254)  
    # phone = models.CharField(default="",max_length=15,validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")])
    address = models.TextField(default="", null=True, blank=True)
    pin = models.IntegerField(default=None,null=True, blank=True)  
    city = models.CharField(max_length=50, default="", null=True, blank=True)
    state = models.CharField(max_length=50, default="", null=True, blank=True)
    pic = models.ImageField(upload_to="uploads/users", null=True, blank=True)
    otp=models.IntegerField(default=None,blank=True,null=True)
    def __str__(self):
        return f"{self.id}  {self.name}  {self.username}"
    
class Wishlist(models.Model):
    id=models.AutoField(primary_key=True)
    product =models.ForeignKey(Product,on_delete=models.CASCADE)
    buyer =models.ForeignKey(Buyer,on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.id)+ " / " + self.buyer.username
    
    
orderStatusOption = [
    (0, "Order is placed"),
    (1, 'Order is packed'),
    (2, 'Dispatched'),
    (3, 'Out For Delivery'),
    (4, 'Delivered')
]
paymentStatusOption = [
    (0, 'Pending'),
    (1, 'Done')
]
paymentModeOption = [
    (0, 'COD'),
    (1, 'NetBanking')
]

class Checkout(models.Model):
    id=models.AutoField(primary_key=True)
    buyer=models.ForeignKey(Buyer,on_delete=models.CASCADE)
    orderstatus=models.IntegerField(choices=orderStatusOption,default=0)
    paymentstatus=models.IntegerField(choices=paymentStatusOption,default=0)
    paymentmode=models.IntegerField(choices=paymentModeOption,default=0)
    subtotal=models.IntegerField()
    shipping=models.IntegerField()
    total=models.IntegerField()
    rpid=models.CharField(max_length=20,default="",null=True,blank=True)
    date=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.id)+" "+self.buyer.username

class CheckoutProduct(models.Model):
    id = models.AutoField(primary_key=True)
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField()
    total = models.IntegerField()
    
    def __str__(self):
        return str(self.id)

class Newslatter(models.Model):
    id=models.AutoField(primary_key=True)
    email=models.EmailField(unique=True,max_length=50)
    
    def __str__(self):
        return str(self.id)+" "+self.email
    
class Contact(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    phone=models.CharField(max_length=15)
    email=models.EmailField(unique=True,max_length=50)
    subject=models.TextField()
    message=models.TextField()
    status=models.BooleanField(default=True)
    date=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.id)+" "+self.email
    
class Testimonial(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=20)
    message=models.TextField()
    pic= models.ImageField(upload_to="upload/testimonial")
    
    def __str__(self):
        return str(self.id)+" / "+self.name