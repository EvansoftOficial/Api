# Generated by Django 3.2.8 on 2023-10-26 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0031_alter_employee_psswd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='psswd',
            field=models.CharField(default='1Q0ED0kQ3rRaHCIqX8qX', max_length=20, unique=True),
        ),
    ]
