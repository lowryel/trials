# Generated by Django 3.2.18 on 2023-05-09 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_booking_subtotal'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='room_image',
            field=models.ImageField(blank=True, null=True, upload_to='media/img'),
        ),
    ]
