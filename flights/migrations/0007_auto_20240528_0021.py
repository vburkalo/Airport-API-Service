from django.db import migrations, models


def populate_code(apps, schema_editor):
    Airport = apps.get_model("flights", "Airport")
    for airport in Airport.objects.all():
        airport.code = "DCA"
        airport.save()


class Migration(migrations.Migration):

    dependencies = [
        ("flights", "0006_airport_code"),
    ]

    operations = [
        migrations.RunPython(populate_code),
    ]
