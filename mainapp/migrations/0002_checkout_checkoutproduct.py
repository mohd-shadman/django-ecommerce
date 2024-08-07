# Generated by Django 5.0.6 on 2024-07-13 04:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('orderstatus', models.IntegerField(choices=[(0, 'Order is placed'), (1, 'Order is packed'), (2, 'Dispatched'), (3, 'Out For Delivery'), (4, 'Delivered')], default=0)),
                ('paymentstatus', models.IntegerField(choices=[(0, 'Pending'), (1, 'Done')], default=0)),
                ('paymentmode', models.IntegerField(choices=[(0, 'COD'), (1, 'NetBanking')], default=0)),
                ('subtotal', models.IntegerField()),
                ('shipping', models.IntegerField()),
                ('total', models.IntegerField()),
                ('rpid', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.buyer')),
            ],
        ),
        migrations.CreateModel(
            name='CheckoutProduct',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('qty', models.IntegerField()),
                ('total', models.IntegerField()),
                ('Checkout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.checkout')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.product')),
            ],
        ),
    ]
