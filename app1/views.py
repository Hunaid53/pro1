from django.shortcuts import render, redirect
from django.http import HttpResponse
from app1.models import *
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.conf import settings

# Create your views here.
def data(request):
    return HttpResponse("<h1>This is my first webpage</h1>")


def index(request):
    a = Category.objects.all()
    return render(request, 'index.html', {'data': a})

def productall(request):
    a = Product.objects.all()
    return render(request, 'product.html', {'data': a})

def productfilter(request, id):
    a = Product.objects.filter(Category = id)
    return render(request, 'product.html', {'data': a})

def productget(request, id):
    a = Product.objects.get(id = id)
    return  render(request, 'product_details.html', {'data': a})

def register(request):
    if request.method != 'POST':
        return render(request,"register.html")
    name1 = request.POST['name']
    email1 = request.POST['email']
    number1 = request.POST['number']
    address1 = request.POST['address']
    password1 = request.POST['password']
    user = Userregister(name = name1, email = email1, number = number1, address = address1, password = password1)
    data = Userregister.objects.filter(email = email1)
    if len(data) != 0:
        return render(request,"register.html", {'m' : 'user already exist!!'})

    user.save()
    return redirect('login')

def login(request):
    if request.method == 'POST':
        email1 = request.POST['email']
        password1 = request.POST['password']
        try:
            if user := Userregister.objects.get(
                email=email1, password=password1
            ):
                request.session['email'] = user.email
                request.session['id'] = user.pk
                print(request.session['id'], request.session['email'])
                return redirect('index1')
            else:
                return  render(request,'login.html', {'m' : 'invalid data entered!!'})
        except Exception:
            return  render(request,'login.html', {'m' : 'invalid data entered!!'})

    return  render(request,'login.html')

def contactus(request):
    if request.method == 'POST':
        name2 = request.POST['name']
        email2 = request.POST['email']
        message2 = request.POST['message']
        user = Contactus(name = name2, email = email2, message = message2)
        user.save()
    return render(request, 'contactus.html')

def logout(request):
    if 'email' in request.session:
        del request.session['email']
        del request.session['id']
    return redirect('login')
        
def profile(request):
    if 'email' not in request.session:
        return redirect('login')
    user = Userregister.objects.get(email = request.session['email'])
    if request.method == 'POST':
        return _extracted_from_profile_(request, user)
    return render(request, 'profile.html', {'user' : user})


# TODO Rename this here and in `profile`
def _extracted_from_profile_(request, user):
    name1 = request.POST['name']
    number1 = request.POST['number']
    address1 = request.POST['address']
    oldpass = request.POST['oldpassword']
    newpass = request.POST['newpassword']
    user.name = name1
    user.number = number1
    user.address = address1
    if oldpass == "" and newpass == "":
        user.save()
        return render(request, 'profile.html', {'user' : user, 'm' : 'Profile updated successfully!!'})
    if user.password != oldpass:
        return render(request, 'profile.html', {'user' : user, 'm' : 'Invalid old password!!'})



    user.password = newpass
    user.save()
    return render(request, 'profile.html', {'user' : user, 'm' : 'Profile updated successfully!!'})



def buynow(request):
    if 'email' not in request.session:
        return redirect('login')
    if  request.method=='POST':
        # model = Order()
        # request.session['userid'] = str(request.session['id'])


        request.session['productid'] = request.POST['productid']
        productdata = Product.objects.get(id = request.POST['productid'])
        request.session['quantity'] = '1'
        request.session['price'] = str((int(request.session['quantity']) * productdata.price))
        request.session['paymentmethod'] = 'Razorpay'
        # request.session['transactionid'] = 'Anbc45622500'
        productdata.quantity -= 1
        # productdata.save()
        # model.save()
        return redirect('razorpayView')
    
    
def ordertable(request):
    if 'email' not in request.session:
        return redirect('login')
    orderdata = Order.objects.filter(userid = request.session['id'])
    productlist = []
    for i in orderdata:
        productdata = Product.objects.get(id = i.productid)
        productdict = {
            'image': productdata.image,
            'name': productdata.name,
            'quantity': i.quantity,
            'price': i.price,
            'date': i.datetime,
            'transactionid': i.transactionid,
        }
        productlist.append(productdict)

    return render(request, 'ordertable.html', {'productlist' : productlist})
    
    
    
def ordersuccess(request):
    if  'email' in request.session:
        return  render(request,'ordersuccess.html')
    else:
        return redirect('login')
    
    

RAZOR_KEY_ID = 'rzp_test_FUHwVUI4XgTIcQ'
RAZOR_KEY_SECRET = 'Y3CxUV49r8eo2vyk7EaS7m8e'
client = razorpay.Client(auth = (RAZOR_KEY_ID, RAZOR_KEY_SECRET))

def razorpayView(request):
    currency = 'INR'
    amount = int(request.session['price'])*100
    # Create a Razorpay Order
    razorpay_order = client.order.create(dict(amount=amount,currency=currency,payment_capture='0'))
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    print(currency)
    print(amount)
    print(razorpay_order)
    print(razorpay_order_id)
    
    callback_url = 'http://127.0.0.1:8000/paymenthandler/'
    # we need to pass these details to frontend.
    context = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': RAZOR_KEY_ID,
        'razorpay_amount': amount,
        'currency': currency,
        'callback_url': callback_url,
    }
    print('exit')
    return render(request,'razorpayDemo.html',context=context)



@csrf_exempt
def paymenthandler(request):
    # only accept POST request.
    print('hello')
    if request.method == "POST":
        print('hello')
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            print(payment_id)
            print(razorpay_order_id)
            print(signature)
            

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # verify the payment signature.
            result = client.utility.verify_payment_signature(
                params_dict)
            print(result)
            
            if result is not None:
                # amount = 20000  # Rs. 200
                amount = int(request.session['price'])*100  # Rs. 200
                print(amount)

                try:
                    # capture the payemt
                    client.payment.capture(payment_id, amount)
                    print('capture')

                    # render success page on successful caputre of payment
                    return render(request, 'ordersuccess.html')

                # except Exception:
                    # print("Hello")
                    # # if we don't find the required parameters in POST data
                    # return HttpResponseBadRequest()
                except Exception as e: print(e)
        except Exception:
                    print("Hello")
                    # if we don't find the required parameters in POST data
                    return HttpResponseBadRequest()
    else:
        print("Hello1")
        # if other than POST request is made.
        return HttpResponseBadRequest()
            
            
            
            

    #         # verify the payment signature.
    #         result = client.utility.verify_payment_signature(
    #             params_dict)

    #         amount = int(request.session['price'])*100  # Rs. 200
    #         # capture the payemt
    #         client.payment.capture(payment_id, amount)


    #         #Order Save Code
    #         orderModel = Order()
    #         orderModel.userid=request.session['id']
    #         orderModel.productid=request.session['productid']
    #         orderModel.quantity=request.session['quantity']
    #         orderModel.price = request.session['price']
    #         orderModel.paymentMethod = request.session['paymentmethod']
    #         orderModel.transactionid = payment_id
    #         productdata=Product.objects.get(id=request.session['productid'])
    #         productdata.quantity=productdata.quantity-int(request.session['quantity'])
    #         productdata.save()
    #         orderModel.save()
    #         del request.session['productid']
    #         del request.session['quantity']
    #         del request.session['price']
    #         del request.session['paymentmethod']
    #         # render success page on successful caputre of payment
    #         return redirect('ordersuccess')
    #     except Exception:
    #         print("Hello")
    #         # if we don't find the required parameters in POST data
    #         return HttpResponseBadRequest()
    # else:
    #     print("Hello1")
    #    # if other than POST request is made.
    #     return HttpResponseBadRequest()
    
    

    #         #Order Save Code
    #         orderModel = Order()
    #         orderModel.userid=request.session['id']
    #         if 'name' in request.session:
    #             print(5555)
    #             orderModel.name=request.session['name']
    #             orderModel.email=request.session['email']
    #             orderModel.number=request.session['number']
    #             orderModel.address=request.session['address']
    #             orderModel.price = request.session['price']
    #             orderModel.paymentmethod = request.session['paymentmethod']
    #             orderModel.transactionid = payment_id
    #             print(5555)
    #             orderModel.productid="0"
    #             print(5555)
    #             orderModel.save()
    #             orderdata=Order.objects.latest('id')
    #             # data=Cart.objects.filter(userid=request.session['id']) and Cart.objects.filter(orderid="0")
    #             for i in data:
    #                 productdata=Product.objects.get(id=i.productid)
    #                 productdata.quantity-=int(i.quantity)
    #                 i.orderid=orderdata.pk
    #                 i.save()
    #                 productdata.save()
    #             del request.session['name']
    #             del request.session['number']
    #             del request.session['address']
    #             del request.session['price']
    #             del request.session['paymentmethod']
            
    #             return redirect('ordersuccess')
    #         else:
    #             userdata=Userregister.objects.get(id=request.session['id'])
    #             orderModel.name=userdata.name
    #             orderModel.email=userdata.email
    #             orderModel.number=userdata.number
    #             orderModel.address=userdata.address
    #             print(111)
    #             orderModel.productid=request.session['productid']
    #             print(2)
    #             orderModel.quantity=request.session['quantity']
    #             print(3)
    #             orderModel.price = request.session['price']
    #             print(4)
    #             orderModel.paymentmethod = "Razorpay"
    #             print('s')
    #             orderModel.transactionid = payment_id
    #             productdata=Product.objects.get(id=request.session['productid'])
    #             productdata.quantity=productdata.quantity-int(request.session['quantity'])
    #             productdata.save()
    #             orderModel.save()
    #             # cartdata=Cart.objects.latest('id')
    #             orderdata=Order.objects.latest('id')
    #             # cartdata.orderid=orderdata.pk
    #             # cartdata.save()
    #             print(111)
                
    #             del request.session['productid']
    #             del request.session['quantity']
    #             del request.session['price']
    #             del request.session['paymentmethod']
                
            
    #             return redirect('ordersuccess')
    #     except:
    #         print("Hello")
    #         # if we don't find the required parameters in POST data
    #         return HttpResponseBadRequest()
    # else:
    #     print("Hello1")
    #    # if other than POST request is made.
    #     return HttpResponseBadRequest()
