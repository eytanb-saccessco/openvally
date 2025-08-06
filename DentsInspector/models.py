from typing import Dict, Any

from django.db import models

class Part(models.Model):
    id = models.IntegerField(primary_key=True)
    part = models.CharField(max_length=30, null=False, blank=False, unique=True)

    class Meta:
        app_label = "DentsInspector"

    @property
    def name(self):
        return self.part

class Location(models.Model):
    id = models.IntegerField(primary_key=True)
    location = models.CharField(max_length=30, null=False, blank=False, unique=True)

    class Meta:
        app_label = "DentsInspector"


    @property
    def name(self):
        return self.location

class DamageType(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=30, null=False, blank=False, unique=True)

    class Meta:
        app_label = "DentsInspector"


    @property
    def name(self):
        return self.type


class Severity(models.Model):
    id = models.IntegerField(primary_key=True)
    severity = models.CharField(max_length=30, null=False, blank=False, unique=True)

    class Meta:
        app_label = "DentsInspector"

    @property
    def name(self):
        return self.severity

class PLDSManager(models.Manager):
    def plds_exists(self, plds_str: str) -> bool:
        try:
            values = plds_str.split('->')

            if len(values) == 4:
                p_id, l_id, d_id, s_id = map(int, values)
            elif len(values) == 3:
                p_id, l_id, d_id = map(int, values)
                s_id = None
            else:
                return False

            return self.filter(p_id=p_id, l_id=l_id, d_id=d_id, s_id=s_id).exists()
        except (ValueError, IndexError):
            return False

    def json(self, plds_str: str) -> Dict[str,Any]:
        values = plds_str.split('->')

        if len(values) == 4:
            p_id, l_id, d_id, s_id = map(int, values)
        elif len(values) == 3:
            p_id, l_id, d_id = map(int, values)
            s_id = None
        else:
            return {}

        return self.get(p_id=p_id, l_id=l_id, d_id=d_id, s_id=s_id).json

    def create_from(self, plds_str: str):
        values = plds_str.split('->')

        if not (3 <= len(values) <= 4):
            raise ValueError(f"Invalid PLDS string format: {plds_str}. Expected 3 or 4 parts.")

        try:
            p_id = int(values[0])
            l_id = int(values[1])
            d_id = int(values[2])
            s_id = int(values[3]) if len(values) == 4 else None
        except ValueError as e:
            raise ValueError(f"Invalid ID in PLDS string '{plds_str}': {e}")

        # Retrieve related objects
        try:
            part_obj = Part.objects.get(id=p_id)
            location_obj = Location.objects.get(id=l_id)
            damage_type_obj = DamageType.objects.get(id=d_id)
            severity_obj = Severity.objects.get(id=s_id) if s_id is not None else None
        except (Part.DoesNotExist, Location.DoesNotExist, DamageType.DoesNotExist, Severity.DoesNotExist) as e:
            raise ValueError(f"Related object not found for PLDS string '{plds_str}': {e}")

        # Use get_or_create to either retrieve an existing instance or create a new one
        plds_instance, created = self.get_or_create(
            p=part_obj,
            l=location_obj,
            d=damage_type_obj,
            s=severity_obj,
        )
        return plds_instance

class PLDS(models.Model):
    p = models.ForeignKey(Part, on_delete=models.CASCADE)
    l = models.ForeignKey(Location, on_delete=models.CASCADE)
    d = models.ForeignKey(DamageType, on_delete=models.CASCADE)
    s = models.ForeignKey(Severity, on_delete=models.CASCADE, null=True)

    objects = PLDSManager()

    class Meta:
        app_label = "DentsInspector"
        unique_together = ("p", "l", "d", "s")

    @property
    def plds(self):
        return f"{self.p}->{self.l}->{self.d}->{self.s}"

    @property
    def pld(self):
        return f"{self.p}->{self.l}->{self.d}"

    @property
    def json(self):
        return {
            "part": self.p.name,
            "location": self.l.name,
            "damage_type": self.d.name,
            "severity": self.s.name,
        }



