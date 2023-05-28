from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from myapp.models import MakeAPost, Booking, Room, BillingProfile, Order, Address
from myapp.forms import CreatePostForm, AddressForm
import datetime

from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
# Create your views here.


def contact(request):

    return render(request, 'contact.html')


def index(request):
    post = MakeAPost.objects.order_by("-date_created")
 
    context = {
        "posts": post,
    }
    return render(request, 'index.html', context)


@login_required(login_url="login")
def vote(request, makeapost_id):
    upvote_an_item = get_object_or_404(MakeAPost, id=makeapost_id)
    
    if request.method == "POST":
        if upvote_an_item.owner != request.user:
            upvote_an_item.upvote += 1
            messages.info(request, f"{request.user} liked your post")
            upvote_an_item.save()
        else:
            upvote_an_item.upvote += 0
            messages.info(request, f"{request.user}, you can't like your own post")
        return HttpResponseRedirect(reverse("index"))

    return render(request, 'vote.html', {"upvote_an_item": upvote_an_item})


@login_required(login_url="login")
def dashboard(request):
    profile = User.objects.get(username=request.user)

    stocks = MakeAPost.objects.filter(owner=request.user)
    context = {
        "stocks": stocks,
        "profile": profile,
    }
    return render(request, "dashboard.html", context)


def upload(request):
    if request.method == "POST":
        post_form = CreatePostForm(request.POST, request.FILES)
       
        if post_form.is_valid():
            post_form.instance.owner = request.user
            post_form.instance.date_created = datetime.datetime.now()
            post_form.instance.upvote = 0
            post_form.save()
    post_form = CreatePostForm()

    context = {
        'form': post_form,
    }
    return render(request, 'upload.html', context)


def room(request):
    rooms = Room.objects.all()
    booking, new_booking = Booking.objects.new_or_get(request)
    # rooms = booking.room.all()
    request.session['booking'] = booking.room.count()

    context = {
        'rooms': rooms, "cart_total_items": request.session['booking']
    }
    return render(request, 'room.html', context)


def booking(request):
    booking, new_booking = Booking.objects.new_or_get(request)
    rooms = booking.room.all()
    request.session["rooms_booked"] = booking.room.count()

    context = {
        "rooms": rooms, "booking": booking, "booking_total": request.session["rooms_booked"],
    }
    # print(booking.total)
    return render(request, 'booking.html', context)


def update_cart(request, pk):
    booking, new_booking = Booking.objects.new_or_get(request)
    room= Room.objects.get(id=pk)

    if room in booking.room.all():
        booking.room.remove(room)
        added = False
        print("removed")
        messages.info(request, f'{room.room_number} already in Cart, removed!')
    else:
        booking.room.add(room)
        added = True
        messages.info(request, f'{room.room_number} booked!')

    request.session['booking_items'] = booking.room.count()
    request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    is_ajax = request.headers.get('X-Requested-With')
    print(is_ajax, 'this is an ajax request')
    if is_ajax:
        if request.method == 'POST':
            print("Ajax request")
            json_data = {
                'added': added,
                'removed': not added,
                'room_total': booking.room.count()
            }
            return JsonResponse(json_data)
        
        return redirect('booking')
    return redirect('room')


def checkout(request):
    form = AddressForm(request.POST)
    booking, new_booking = Booking.objects.new_or_get(request)
    rooms = booking.room.all()
    user = request.user
    billing = None
    if request.user.is_authenticated:
        billing, created = BillingProfile.objects.get_or_create(user=user, email=user.email)
    else:
        return redirect("login")


    order_obj=None
    address_qs = None
    address_id = request.session.get('address_id', None)

    if billing is not None:
        order = Order.objects.filter(billing_profile=billing, booking=booking, active=True)
        if order.count()==1:
            order_obj = order.first()
        else:
            order_obj = Order.objects.create(billing_profile=billing, booking=booking)

        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing)
        if address_id:
            order_obj.address = Address.objects.get(id=address_id)
            del request.session["address_id"]
        if address_id:
            order_obj.save()

    if request.method == "POST":
        "some check that order is done"
        if order_obj.check_done():
            request.session['booking_items'] = 0
            del request.session['booking_id']
            return redirect('success')
    context = {
        'billing': billing, 
        "rooms": rooms, 
        "form": form, 
        "address": address_qs, 
        "booking":booking,
    }
    return render(request, "checkout.html", context)


def delete_booking(request, pk):
    booking, new_booking = Booking.objects.new_or_get(request)
    rooms = Room.objects.get(id=pk)
    if rooms in booking.room.all():
        booking.room.remove(rooms)

        return redirect("booking")
    return redirect("booking")


def checkout_address_create_view(request):
    form=AddressForm(request.POST or None)
    if form.is_valid():
        instance=form.save(commit=False)
        billing_profile=None
        user = request.user
        if request.user.is_authenticated:
            billing_profile, created=BillingProfile.objects.get_or_create(user=user, email=user.email)
        else:
            pass

        if billing_profile is not None:
            instance.billing_profile = billing_profile
            instance.save()
            request.session["address_id"] = instance.id
            return redirect('checkout')
    return redirect('checkout')


def use_existing_delivery_address(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            user = request.user
            address_id = request.POST.get("address", None)
            billing, created = BillingProfile.objects.get_or_create(user=user, email=user.email)
            print("existing address", address_id)
            if address_id is not None:
                print(address_id)
                qs = Address.objects.filter(billing_profile=billing, id=address_id)
                print(qs)
                if qs.exists():
                    address = address_id
                return redirect('checkout')
            print("NOOOOOOOOOOOOOONE")
    return redirect('checkout')


# def provide_new_delivery_address(request):
    # if request.user.is_authenticated:
    #     form = AddressForm(request.POST or None)
    #     if form.is_valid():
    #         address = form.save(commit=False)
    #         address.user = request.user
    #         address.save()
    #         return redirect('checkout')
    #     else:
    #         context = {
    #             'form': form,
    #         }
    #         return render(request, 'provide_new_delivery_address.html', context)
    # else:
    #     return redirect('login')


# def upload(request):
#     context = {}
#     if request.method == 'POST':
#         uploaded_file = request.FILES['document']
#         fs = FileSystemStorage()
#         name = fs.save(uploaded_file.name, uploaded_file)
#         context['url'] = fs.url(name)
#     uploaded_file = ""
#     return render(request, 'upload.html', context)


def signup(request):
    if request.method == 'POST':
        Username = request.POST['Username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already Used')
                return redirect('signup')
            elif User.objects.filter(username=Username).exists():
                messages.info(request, 'Username already Used')
                return redirect('signup')
            else:
                user = User.objects.create_user(
                    username=Username, email=email, password=password)
                user.save()
                messages.info(request, "Signup Successful")
                return redirect('login/')
        else:
            messages.info(request, 'Password Incorrect')
            return redirect('signup')
    return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Credentials invalid')
            return redirect('login')
    return render(request, 'login.html')


def logout_view(request):
    auth.logout(request)
    return redirect("index")
