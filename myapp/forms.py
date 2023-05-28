from django.forms import ModelForm
from .models import MakeAPost, Address

class CreatePostForm(ModelForm):
    class Meta:
        model = MakeAPost
        fields = [ 'name', 'image', 'description']

class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ['line1', 'line2', 'city', 'state', 'postal_code']
        # excludes = ['billing_profile']

# class AddressForm(ModelForm):
#     class Meta:
#         model = Address
#         fields = ['line1', 'line2', 'city', 'state', 'postal_code']
#         # excludes = ['billing_profile']
