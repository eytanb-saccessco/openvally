# DentsInspector/migrations/000X_auto_YYYYMMDD_HHMM.py (replace X, YYYYMMDD_HHMM with actual values)

from django.db import migrations


def populate_location_data(apps, schema_editor):
    """
    Populates the Location model with initial data.
    """
    Location = apps.get_model('DentsInspector', 'Location')

    locations_to_create = [
        {'id': 0, 'location': 'all'},
        {'id': 4, 'location': 'left-front'},
        {'id': 5, 'location': 'left-rear'},
        {'id': 6, 'location': 'right-front'},
        {'id': 7, 'location': 'right-rear'},
        {'id': 1, 'location': 'center-front'},
        {'id': 2, 'location': 'center-rear'},
        {'id': 3, 'location': 'left-side'},
        {'id': 8, 'location': 'right-side'},
        {'id': 29, 'location': 'center'},
        {'id': 12, 'location': 'left-row3'},
        {'id': 13, 'location': 'right-row3'},
        {'id': 11, 'location': 'center-row3'},
        {'id': 32, 'location': 'warning-light'},
        {'id': 37, 'location': 'underhood'},
    ]

    for data in locations_to_create:
        Location.objects.create(**data)


def reverse_location_data(apps, schema_editor):
    """
    Deletes the Location data created by populate_location_data.
    """
    Location = apps.get_model('DentsInspector', 'Location')
    # Delete all locations that were created by this migration
    Location.objects.filter(id__in=[
        0, 4, 5, 6, 7, 1, 2, 3, 8, 29, 12, 13, 11, 32, 37
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('DentsInspector', '0002_populate_parts'),
        # Ensure this points to your latest schema migration (e.g., the Part data migration)
    ]

    operations = [
        migrations.RunPython(populate_location_data, reverse_location_data),
    ]