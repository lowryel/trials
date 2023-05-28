# Generated by Django 3.2.18 on 2023-05-20 08:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0021_auto_20230520_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booked', to='myapp.booking'),
        ),
    ]
