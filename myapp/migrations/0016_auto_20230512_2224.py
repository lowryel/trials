# Generated by Django 3.2.18 on 2023-05-12 22:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0015_auto_20230509_1529'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line1', models.CharField(max_length=120)),
                ('city', models.CharField(max_length=120)),
                ('state', models.CharField(max_length=120)),
                ('postal_code', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='BillingProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('active', models.BooleanField(default=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('created', 'Created'), ('paid', 'Paid'), ('refunded', 'Refunded'), ('shipped', 'Shipped')], default='created', max_length=120)),
                ('active', models.BooleanField(default=True)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.address')),
                ('billing_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.billingprofile')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booked', to='myapp.booking')),
            ],
        ),
        migrations.AddField(
            model_name='address',
            name='billing_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.billingprofile'),
        ),
    ]
