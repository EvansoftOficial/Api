# Generated by Django 3.2.8 on 2024-06-24 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0129_alter_branch_psswd'),
        ('inventory', '0013_auto_20240509_0845'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='company.branch'),
        ),
    ]
