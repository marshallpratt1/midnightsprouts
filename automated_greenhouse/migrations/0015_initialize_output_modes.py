from django.db import migrations


def initialize(apps, schema_editor):
    status = apps.get_model('automated_greenhouse', 'SystemStatus').objects.last()
    automatic = status.automatic if status else True
    Control = apps.get_model('automated_greenhouse', 'OutputControl')
    for name in ('nursery_heater', 'water_heater', 'fan', 'vent', 'pump',
                 'garden_valve', 'greenhouse_planter_valve', 'greenhouse_tree_valve'):
        Control.objects.get_or_create(name=name, defaults={'automatic': automatic})


class Migration(migrations.Migration):
    dependencies = [('automated_greenhouse', '0014_alertnotification_outputcontrol_sensorhealth')]
    operations = [migrations.RunPython(initialize, migrations.RunPython.noop)]
