from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='FuelStation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opis_truckstop_id', models.CharField(max_length=64, db_index=True)),
                ('truckstop_name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=512)),
                ('city', models.CharField(max_length=128, db_index=True)),
                ('state', models.CharField(max_length=16, db_index=True)),
                ('rack_id', models.CharField(blank=True, max_length=64, null=True, db_index=True)),
                ('retail_price', models.DecimalField(max_digits=6, decimal_places=3, db_index=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('is_geocoded', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Fuel Station',
                'verbose_name_plural': 'Fuel Stations',
            },
        ),
    ]

