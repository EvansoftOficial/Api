# Generated by Django 3.2.8 on 2024-02-21 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0100_alter_branch_psswd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='psswd',
            field=models.CharField(default='BZzS7ZSs8c', max_length=10),
        ),
    ]
