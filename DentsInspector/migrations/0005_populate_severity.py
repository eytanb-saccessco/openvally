# DentsInspector/migrations/000X_auto_YYYYMMDD_HHMM.py (replace X, YYYYMMDD_HHMM with actual values)

from django.db import migrations


def populate_severity_data(apps, schema_editor):
    """
    Populates the Severity model with initial data.
    """
    Severity = apps.get_model('DentsInspector', 'Severity')

    severities_to_create = [
        {'id': 1, 'severity': 'small'},
        {'id': 3, 'severity': 'large'},
        {'id': 2, 'severity': 'medium'},
        {'id': 4, 'severity': 'replacement-required'},
    ]

    for data in severities_to_create:
        Severity.objects.create(**data)


def reverse_severity_data(apps, schema_editor):
    """
    Deletes the Severity data created by populate_severity_data.
    """
    Severity = apps.get_model('DentsInspector', 'Severity')
    # Delete all severities that were created by this migration
    Severity.objects.filter(id__in=[1, 3, 2, 4]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('DentsInspector', '0004_populate_damage_types'),
        # Ensure this points to your latest schema migration (e.g., the DamageType data migration)
    ]

    operations = [
        migrations.RunPython(populate_severity_data, reverse_severity_data),
    ]