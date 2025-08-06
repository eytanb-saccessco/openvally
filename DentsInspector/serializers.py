from rest_framework import serializers
from .models import Part, Location, DamageType, Severity  # Import your Part model

class AbstractSerializer(serializers.ModelSerializer):
    model = None
    field = None
    @classmethod
    def all(cls):
        if cls.model is None:
            raise NotImplementedError()
        queryset = cls.model.objects.all()
        data = [{str(x.id): getattr(x, cls.field)} for x in queryset]
        return {"parts": data}


class PartSerializer(AbstractSerializer):
    model = Part
    field = 'part'

class LocationSerializer(AbstractSerializer):
    model = Location
    field = 'location'

class DamageTypeSerializer(AbstractSerializer):
    model = DamageType
    field = 'type'

class SeveritySerializer(AbstractSerializer):
    model = Severity
    field = 'severity'
