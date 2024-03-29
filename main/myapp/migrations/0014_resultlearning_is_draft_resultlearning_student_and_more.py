# Generated by Django 5.0.1 on 2024-02-05 20:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_resultlearning'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultlearning',
            name='is_draft',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='resultlearning',
            name='student',
            field=models.ForeignKey(limit_choices_to={'role': 'student'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resultlearning_as_student', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='resultlearning',
            name='study_class',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.studyclass'),
        ),
    ]
