# Generated by Django 3.2.8 on 2024-09-11 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0136_alter_employee_psswd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='psswd',
            field=models.CharField(default='S9jJyCyj5q7GKOxxD5ea', max_length=20, unique=True),
        ),
    ]
