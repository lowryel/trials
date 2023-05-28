from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_out


class MakeAPost(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=64, blank=True)
    upvote = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="media", blank=True, null=True)
    description = models.TextField(max_length=512, blank=True, null=True, default="")

    def __str__(self):
        return self.name
    
    @property
    def imageUrl(self):
        try:
            url = self.image.url
        except:
            url=''
        return url


class Room(models.Model):
    room_number = models.CharField(max_length=25, unique=True)
    fee = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    room_image   = models.ImageField(upload_to="media/img", null=True, blank=True)
    description = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.room_number

    @property
    def imageUrl(self):
        try:
            url = self.room_image.url
        except:
            url=''
        return url
    


class  BookingManager(models.Manager):
    def new_or_get(self, request):
        booking_id=request.session.get("booking_id", None)
        qs = self.get_queryset().filter(id=booking_id)
        countqs = qs.count()
        if countqs == 1:
            new_booking = False
            booking_obj = qs.first()
            if request.user.is_authenticated and booking_obj.user is None:
                booking_obj.user = request.user
                booking_obj.save()
        else:
            # This will handle the authenticated user
            booking_obj = Booking.objects.new_booking_obj(user=request.user)
            new_booking = True
            request.session['booking_id'] = booking_obj.id
        return booking_obj, new_booking

    def new_booking_obj(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)


class Booking(models.Model):
    user         = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    slug         = models.UUIDField(default=uuid.uuid4, unique=True)
    room         = models.ManyToManyField(Room, blank=True)
    update       = models.DateField(auto_now=True, null=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    subtotal     = models.CharField(max_length=10, default=0)
    total        = models.CharField(max_length=10, default=0)
    objects      = BookingManager()

    def __str__(self):
        return str(self.id)


def booking_m2m_changed_receiver(sender, instance, action, *args, **kwargs):
    if action=="post_add" or action=="post_remove" or action=="post_clear":

        ordered_room = instance.room.all()
        booking_total = 0
        for item in ordered_room:
            booking_total += item.fee
        instance.subtotal=booking_total
        instance.save()
        return instance.subtotal

m2m_changed.connect(booking_m2m_changed_receiver, sender=Booking.room.through)


@receiver(pre_save, sender=Booking)
def set_subtotal_to_total(sender, instance, created=False, *args, **kwargs):
    # set total to subtotal
    instance.total = float(instance.subtotal)
    instance.total -= 14.99
    print(instance.total, 'booking total after discount')


# @receiver(user_logged_out)
# def delete_cart(sender, user, request, **kwargs):
#     # Delete the cart for the user
#     Booking.objects.filter(user=user).delete()


class BillingProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    

def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)
post_save.connect(user_created_receiver, sender=User)


class Address(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    line1 = models.CharField(max_length=120)
    line2 = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=120)

    def __str__(self):
        return str(self.billing_profile)

@receiver(pre_save, sender=Address)
def pre_assign_address_id(sender, instance, created=False, *args, **kwargs):
    if instance is not None:
        addressid=instance.objects.get(id=kwargs["id"])
        print(addressid)


ORDER_STATUS_CHOICES=(
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('refunded', 'Refunded'),
    ('shipped', 'Shipped'),
)

#Bard generated
class Order(models.Model):
    """A model for a cart order."""

    billing_profile = models.ForeignKey(
        BillingProfile,
        on_delete=models.CASCADE,
    )
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='booked'
    )
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=120, default='created', 
                              choices=ORDER_STATUS_CHOICES)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        """Returns the total cost of the order."""
        new_total_cost = self.booking.total
        formatted_total = new_total_cost
        self.total_cost = formatted_total
        self.save()
        return new_total_cost

    def check_done(self):
        billing_profile=self.billing_profile
        address = self.address
        total = self.total_cost
        if billing_profile and address and total >0:
            return True
        return False


def post_save_cart_total(sender, created, instance, *args, **kwargs):
    if not created:
        booking_obj=instance
        booking_total=booking_obj.total
        booking_id=booking_obj.id
        print(booking_id)
        qs=Order.objects.filter(booking__id=booking_id)
        if qs.count() == 1:
            order_obj=qs.first()
            order_obj.get_total_cost()

post_save.connect(post_save_cart_total, sender=Booking)


def post_save_order(sender, instance, created, *args, **kwargs):
    if created:
        instance.get_total_cost()
post_save.connect(post_save_order, sender=Order)


# @receiver(pre_save, sender=Booking)
# def generate_user_token(sender, instance, created=False, *args, **kwargs):


