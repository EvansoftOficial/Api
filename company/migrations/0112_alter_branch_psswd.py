# Generated by Django 3.2.8 on 2024-03-16 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0111_alter_branch_psswd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='psswd',
            field=models.CharField(default='xfdPHOJDXX', max_length=10),
        ),
    ]
