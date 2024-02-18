# Generated by Django 5.0.1 on 2024-02-09 07:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0020_alter_resultlearning_final_score_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scorecolumn',
            name='score',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)]),
        ),
    ]