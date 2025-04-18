# Generated by Django 5.0.2 on 2025-03-18 10:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Medicine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='inventory',
            options={},
        ),
        migrations.AlterModelOptions(
            name='prescription',
            options={},
        ),
        migrations.AlterModelOptions(
            name='prescriptionitem',
            options={},
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='batch_number',
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='drug',
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='expiry_date',
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='unit_price',
        ),
        migrations.RemoveField(
            model_name='prescription',
            name='diagnosis',
        ),
        migrations.RemoveField(
            model_name='prescription',
            name='doctor',
        ),
        migrations.RemoveField(
            model_name='prescription',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='prescriptionitem',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='prescriptionitem',
            name='drug',
        ),
        migrations.RemoveField(
            model_name='prescriptionitem',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='prescriptionitem',
            name='frequency',
        ),
        migrations.RemoveField(
            model_name='prescriptionitem',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='inventory',
            name='min_quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='inventory',
            name='unit',
            field=models.CharField(default='viên', max_length=50),
        ),
        migrations.AddField(
            model_name='prescription',
            name='pharmacist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pharmacist_prescriptions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient_prescriptions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='status',
            field=models.CharField(choices=[('pending', 'Chờ xử lý'), ('processing', 'Đang xử lý'), ('completed', 'Hoàn thành')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='prescriptionitem',
            name='dosage',
            field=models.CharField(default='1 viên/lần', max_length=200),
        ),
        migrations.AlterField(
            model_name='prescriptionitem',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='prescriptionitem',
            name='prescription',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='pharmacy.prescription'),
        ),
        migrations.AlterField(
            model_name='prescriptionitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='inventory',
            name='medicine',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pharmacy.medicine'),
        ),
        migrations.AddField(
            model_name='prescriptionitem',
            name='medicine',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pharmacy.medicine'),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('sale', 'Bán hàng'), ('purchase', 'Nhập hàng'), ('return', 'Trả hàng')], default='sale', max_length=20)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('prescription', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmacy.prescription')),
            ],
        ),
    ]
