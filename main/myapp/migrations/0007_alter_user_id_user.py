# Generated by Django 5.0.1 on 2024-02-05 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_alter_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id_user',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
