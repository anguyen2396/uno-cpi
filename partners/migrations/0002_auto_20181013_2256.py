# Generated by Django 2.1.1 on 2018-10-14 03:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('partners', '0001_initial'),
        ('university', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='campuspartner',
            name='college_name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='university.College'),
        ),
        migrations.AddField(
            model_name='campuspartner',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='university.Department'),
        ),
        migrations.AddField(
            model_name='campuspartner',
            name='education_system',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='university.EducationSystem'),
        ),
        migrations.AddField(
            model_name='campuspartner',
            name='university',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='university.University'),
        ),
    ]
