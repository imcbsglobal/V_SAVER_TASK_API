from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from .models import AccMaster, Misel, AccInvMast


# ── AccMaster ─────────────────────────────────────────────

class AccMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model            = AccMaster
        fields           = ['code', 'name', 'place', 'exregnodate', 'super_code', 'phone2', 'client_id', 'synced_at']
        read_only_fields = ['synced_at']


class BulkAccMasterSerializer(serializers.Serializer):
    records   = serializers.ListField(child=serializers.DictField())
    client_id = serializers.CharField(max_length=50)

    def create(self, validated_data):
        records   = validated_data['records']
        client_id = validated_data['client_id']
        now       = timezone.now()
        objs = [
            AccMaster(
                code        = r['code'],
                name        = r['name'],
                place       = r.get('place'),
                exregnodate = r.get('exregnodate'),
                super_code  = r.get('super_code'),
                phone2      = r.get('phone2'),
                client_id   = client_id,
                synced_at   = now,
            )
            for r in records
        ]
        existing = set(AccMaster.objects.filter(
            code__in=[o.code for o in objs]
        ).values_list('code', flat=True))
        with transaction.atomic():
            AccMaster.objects.bulk_create(
                objs,
                update_conflicts=True,
                unique_fields=['code'],
                update_fields=['name', 'place', 'exregnodate', 'super_code', 'phone2', 'client_id', 'synced_at'],
            )
        created = sum(1 for o in objs if o.code not in existing)
        return {'created': created, 'updated': len(objs) - created, 'total': len(records)}


# ── Misel ─────────────────────────────────────────────────

class MiselSerializer(serializers.ModelSerializer):
    class Meta:
        model            = Misel
        fields           = ['id', 'firm_name', 'address1', 'client_id', 'synced_at']
        read_only_fields = ['synced_at']


class BulkMiselSerializer(serializers.Serializer):
    records   = serializers.ListField(child=serializers.DictField())
    client_id = serializers.CharField(max_length=50)

    def create(self, validated_data):
        records   = validated_data['records']
        client_id = validated_data['client_id']
        created = updated = 0
        for rec in records:
            _, is_new = Misel.objects.update_or_create(
                firm_name=rec.get('firm_name'),
                client_id=client_id,
                defaults={
                    **{k: v for k, v in rec.items() if k != 'firm_name'},
                    'client_id': client_id,
                }
            )
            if is_new: created += 1
            else:      updated += 1
        return {'created': created, 'updated': updated, 'total': len(records)}


# ── AccInvMast ────────────────────────────────────────────

class AccInvMastSerializer(serializers.ModelSerializer):
    class Meta:
        model            = AccInvMast
        fields           = ['slno', 'invdate', 'customerid', 'nettotal', 'client_id', 'synced_at']
        read_only_fields = ['synced_at']


class BulkAccInvMastSerializer(serializers.Serializer):
    records   = serializers.ListField(child=serializers.DictField())
    client_id = serializers.CharField(max_length=50)

    def create(self, validated_data):
        records   = validated_data['records']
        client_id = validated_data['client_id']
        now       = timezone.now()
        objs = [
            AccInvMast(
                slno       = r['slno'],
                invdate    = r.get('invdate'),
                customerid = r.get('customerid'),
                nettotal   = r.get('nettotal'),
                client_id  = client_id,
                synced_at  = now,
            )
            for r in records
        ]
        existing = set(AccInvMast.objects.filter(
            slno__in=[o.slno for o in objs]
        ).values_list('slno', flat=True))
        with transaction.atomic():
            AccInvMast.objects.bulk_create(
                objs,
                update_conflicts=True,
                unique_fields=['slno'],
                update_fields=['invdate', 'customerid', 'nettotal', 'client_id', 'synced_at'],
            )
        created = sum(1 for o in objs if o.slno not in existing)
        return {'created': created, 'updated': len(objs) - created, 'total': len(records)}