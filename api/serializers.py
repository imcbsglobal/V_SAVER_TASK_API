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
        created = updated = 0

        # Use update_or_create scoped strictly to (code + client_id)
        for r in records:
            _, is_new = AccMaster.objects.update_or_create(
                code      = r['code'],
                client_id = client_id,
                defaults  = {
                    'name'       : r['name'],
                    'place'      : r.get('place'),
                    'exregnodate': r.get('exregnodate'),
                    'super_code' : r.get('super_code'),
                    'phone2'     : r.get('phone2'),
                    'synced_at'  : now,
                }
            )
            if is_new: created += 1
            else:      updated += 1

        return {'created': created, 'updated': updated, 'total': len(records)}


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
                firm_name = rec.get('firm_name'),
                client_id = client_id,
                defaults  = {
                    'address1' : rec.get('address1'),
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
        created = updated = 0

        # Use update_or_create scoped strictly to (slno + client_id)
        for r in records:
            _, is_new = AccInvMast.objects.update_or_create(
                slno      = r['slno'],
                client_id = client_id,
                defaults  = {
                    'invdate'   : r.get('invdate'),
                    'customerid': r.get('customerid'),
                    'nettotal'  : r.get('nettotal'),
                    'synced_at' : now,
                }
            )
            if is_new: created += 1
            else:      updated += 1

        return {'created': created, 'updated': updated, 'total': len(records)}