# Generated by Django 4.2 on 2023-05-05 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_alter_booking_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='makeapost',
            name='description',
            field=models.TextField(blank=True, default='', max_length=512, null=True),
        ),
    ]
