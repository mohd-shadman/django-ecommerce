from django.contrib import admin
from .models import*

# Register your models here.

# admin.site.register((MainCategory,SubCategory,Brand,Product,Buyer,Wishlist,Checkout,CheckoutProduct,Newslatter,Contact))

@admin.register((MainCategory))
class MaincategoryAdmin(admin.ModelAdmin):
    list_display=("id","name")
    
@admin.register((SubCategory))
class SubcategoryAdmin(admin.ModelAdmin):
    list_display=("id","name")
    
    
@admin.register((Brand))
class BrandAdmin(admin.ModelAdmin):
    list_display=("id","name")
    
@admin.register((Product))
class ProductAdmin(admin.ModelAdmin):
    list_display=("id","name","maincategory","subcategory","brand","baseprice","discount","finalprice","color","size","pic1")
    
@admin.register((Buyer))
class BuyerAdmin(admin.ModelAdmin):
    list_display=("id","name","username","email","address")
    
@admin.register((Wishlist))
class WishlistAdmin(admin.ModelAdmin):
    list_display=("id","product","buyer")
    
@admin.register((Checkout))
class CheckoutAdmin(admin.ModelAdmin):
    list_display=("id","buyer","orderstatus","paymentstatus","paymentmode","subtotal","shipping","total")
    
@admin.register((CheckoutProduct))
class ChecoutproductAdmin(admin.ModelAdmin):
    list_display=("id","checkout","product","qty","total")
    
@admin.register((Newslatter))
class NewslatterAdmin(admin.ModelAdmin):
    list_display=("id","email")
    
@admin.register((Contact))
class ContactAdmin(admin.ModelAdmin):
    list_display=("id","name","phone","email","subject","message")
    
@admin.register((Testimonial))
class TestimonialAdmin(admin.ModelAdmin):
    list_display=("id","name","message","pic")