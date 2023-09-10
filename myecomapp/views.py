from django.shortcuts import render, redirect
from myecomapp.models import Contact, Product, Orders, OrderUpdate
from django.contrib import messages
from math import ceil
from myecomapp import keys
from django.conf import settings
MERCHANT_KEY=keys.MK
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum
# import razorpay
# Create your views here.

def index(request):
    current_user = request.user
    print(current_user)
    allProds = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}
    return render(request,'index.html',params)
    


def about(request):
    return render (request,"about.html")




def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    currentuser = request.user.username
    items = Orders.objects.filter(email=currentuser)

    for item in items:
        myid = item.oid
        rid = myid.replace("SlayOn", " ")

        # Convert rid to integer (assuming it's a valid integer)
        try:
            rid_int = int(rid)
            status = OrderUpdate.objects.filter(order_id=rid_int)
            item.status_info = status  # Store the status info in the item instance
        except ValueError:
            # Handle the case where rid is not a valid integer
            item.status_info = None  # Add a placeholder or handle it as needed

    context = {"items": items, "currentuser": currentuser}
    return render(request, "profile.html", context)



def contact(request):
    # if not request.user.is_authenticated:
    #     messages.warning(request,"Login & Try Again")
    #     return redirect('/login')
    if request.method=="POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        pnumber = request.POST.get('pnumber')
        desc = request.POST.get('desc')
        myquery=Contact(name=name,email=email,desc=desc,phone=pnumber)
        myquery.save()
        messages.success(request,"Thanks for your response, We'll get back to you soon...")
  
  
    return render(request, 'contact.html')

def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/login')
    if request.method=="POST":
       

        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2','')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
         

        Order = Orders(items_json=items_json,name=name,amount=amount, 
                       email=email, address1=address1,address2=address2,city=city,
                       state=state,zip_code=zip_code,phone=phone)
        print(amount)
        Order.save()
        update = OrderUpdate(order_id=Order.order_id,update_desc="the order has been placed")
        update.save()
        thanks = True
        id = Order.order_id
        oid=str(id)
        oid=str(id)
        param_dict = {

            'MID': 'add ur merchant id',
            'ORDER_ID': oid,
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'paytm.html', {'param_dict': param_dict})
       

    return render(request, 'checkout.html')


@csrf_exempt
def handlerequest(request):

    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
            a=response_dict['ORDERID']
            b=response_dict['TXNAMOUNT']
            # rid=a.replace("slayon","")
           
            # print(rid)
            # filter2= Orders.objects.filter(order_id=rid)
            filter2= Orders.objects.filter(order_id=a)
            print(filter2)
            print(a,b)
            for post1 in filter2:

                post1.oid=a
                post1.amountpaid=b
                post1.paymentstatus="PAID"
                post1.save()
            print("run agede function")
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'paymentstatus.html', {'response': response_dict})


