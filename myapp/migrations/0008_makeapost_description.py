# Generated by Django 4.2 on 2023-04-07 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0007_makeapost_image_alter_makeapost_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="makeapost",
            name="description",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
