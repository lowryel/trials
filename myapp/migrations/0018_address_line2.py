# Generated by Django 3.2.18 on 2023-05-16 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_alter_billingprofile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='line2',
            field=models.CharField(default=1, max_length=120),
            preserve_default=False,
        ),
    ]
