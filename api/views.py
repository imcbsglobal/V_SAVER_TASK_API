from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AccMaster, Misel, AccInvMast
from .serializers import (
    AccMasterSerializer, BulkAccMasterSerializer,
    MiselSerializer, BulkMiselSerializer,
    AccInvMastSerializer, BulkAccInvMastSerializer,
)


# ── Health ────────────────────────────────────────────────

class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'time': timezone.now()})


# ── AccMaster (Debtors) ───────────────────────────────────

class AccMasterListView(APIView):
    def get(self, request):
        client_id = request.query_params.get('client_id')
        qs = AccMaster.objects.all()
        if client_id:
            qs = qs.filter(client_id=client_id)
        serializer = AccMasterSerializer(qs, many=True)
        return Response(serializer.data)


class AccMasterDetailView(APIView):
    def get(self, request, code):
        try:
            obj = AccMaster.objects.get(pk=code)
        except AccMaster.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AccMasterSerializer(obj).data)


class AccMasterBulkView(APIView):
    def post(self, request):
        serializer = BulkAccMasterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)


class AccMasterTruncateView(APIView):
    def delete(self, request):
        client_id = request.query_params.get('client_id')
        qs = AccMaster.objects.all()
        if client_id:
            qs = qs.filter(client_id=client_id)
        count, _ = qs.delete()
        return Response({'deleted': count})


# ── Misel (Firm Info) ─────────────────────────────────────

class MiselListView(APIView):
    def get(self, request):
        client_id = request.query_params.get('client_id')
        qs = Misel.objects.all()
        if client_id:
            qs = qs.filter(client_id=client_id)
        serializer = MiselSerializer(qs, many=True)
        return Response(serializer.data)


class MiselBulkView(APIView):
    def post(self, request):
        serializer = BulkMiselSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)


class MiselTruncateView(APIView):
    def delete(self, request):
        client_id = request.query_params.get('client_id')
        qs = Misel.objects.all()
        if client_id:
            qs = qs.filter(client_id=client_id)
        count, _ = qs.delete()
        return Response({'deleted': count})


# ── AccInvMast (Invoices) ─────────────────────────────────

class AccInvMastListView(APIView):
    def get(self, request):
        client_id   = request.query_params.get('client_id')
        customerid  = request.query_params.get('customerid')
        qs = AccInvMast.objects.all()
        if client_id:
            qs = qs.filter(client_id=client_id)
        if customerid:
            qs = qs.filter(customerid=customerid)
        serializer = AccInvMastSerializer(qs, many=True)
        return Response(serializer.data)


class AccInvMastDetailView(APIView):
    def get(self, request, slno):
        try:
            obj = AccInvMast.objects.get(pk=slno)
        except AccInvMast.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AccInvMastSerializer(obj).data)


class AccInvMastBulkView(APIView):
    def post(self, request):
        serializer = BulkAccInvMastSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)


class AccInvMastSummaryView(APIView):
    def get(self, request):
        client_id  = request.query_params.get('client_id')
        customerid = request.query_params.get('customerid')
        qs = AccInvMast.objects.all()
        if client_id:
            qs = qs.filter(client_id=client_id)

        # Single customer summary
        if customerid:
            qs = qs.filter(customerid=customerid)
            agg = qs.aggregate(
                total_sales=Sum('nettotal'),
                invoice_count=Count('slno'),
            )
            return Response({
                'customerid':    customerid,
                'total_sales':   agg['total_sales'] or 0,
                'invoice_count': agg['invoice_count'] or 0,
            })

        # All-customers summary (original behaviour)
        summary = qs.aggregate(
            total_invoices=Count('slno'),
            total_amount=Sum('nettotal'),
        )
        return Response(summary)


class AccInvMastSummaryView(APIView):
    def get(self, request):
        client_id  = request.query_params.get('client_id')
        customerid = request.query_params.get('customerid')
        qs = AccInvMast.objects.all()
        if client_id:
            qs = qs.filter(client_id=client_id)

        # Single customer summary
        if customerid:
            qs = qs.filter(customerid=customerid)
            agg = qs.aggregate(
                total_sales=Sum('nettotal'),
                invoice_count=Count('slno'),
            )
            return Response({
                'customerid':    customerid,
                'total_sales':   agg['total_sales'] or 0,
                'invoice_count': agg['invoice_count'] or 0,
            })

        # All-customers summary
        summary = qs.aggregate(
            total_invoices=Count('slno'),
            total_amount=Sum('nettotal'),
        )
        return Response(summary)