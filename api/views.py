import logging
from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AccMaster, Misel, AccInvMast
from .serializers import (
    AccMasterSerializer, BulkAccMasterSerializer,
    MiselSerializer, BulkMiselSerializer,
    AccInvMastSerializer, BulkAccInvMastSerializer,
)

logger = logging.getLogger(__name__)


def _require_client_id(request):
    """
    Return (client_id, None) if present, or (None, error_response).

    Checks in this order:
      1. ?client_id= query param       <- most reliable, always works
      2. X-Client-ID request header
      3. request.data body             <- works on DELETE only when the view
                                          declares parser_classes (see truncate views)

    NOTE: DRF does NOT parse DELETE bodies by default — truncate views
    override parser_classes so all three sources work.
    """
    client_id = (
        request.query_params.get('client_id', '').strip()
        or request.headers.get('X-Client-ID', '').strip()
    )
    # Body fallback — only effective when view declares parser_classes
    if not client_id and hasattr(request, 'data') and isinstance(request.data, dict):
        client_id = request.data.get('client_id', '').strip()

    if not client_id:
        logger.warning(
            f"[AUTH] client_id missing — "
            f"query={request.query_params.get('client_id', '')!r}, "
            f"header={request.headers.get('X-Client-ID', '')!r}, "
            f"method={request.method}"
        )
        return None, Response(
            {'error': 'client_id is required. Pass as ?client_id=... or X-Client-ID header.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    return client_id, None


def _require_client_id(request):
    """
    Return (client_id, None) if present, or (None, error_response).
    Checks query params first, then X-Client-ID header.
    """
    client_id = (
        request.query_params.get('client_id', '').strip()
        or request.headers.get('X-Client-ID', '').strip()
    )
    if not client_id:
        return None, Response(
            {'error': 'client_id is required. Pass as ?client_id=... or X-Client-ID header.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    return client_id, None


# ── Health ────────────────────────────────────────────────

class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'time': timezone.now()})


# ── AccMaster (Debtors) ───────────────────────────────────

class AccMasterListView(APIView):
    def get(self, request):
        client_id, err = _require_client_id(request)
        if err:
            return err
        qs = AccMaster.objects.filter(client_id=client_id)
        serializer = AccMasterSerializer(qs, many=True)
        return Response(serializer.data)


class AccMasterDetailView(APIView):
    def get(self, request, code):
        client_id, err = _require_client_id(request)
        if err:
            return err
        try:
            # FIX: scope by both code AND client_id (pk is auto id, not code)
            obj = AccMaster.objects.get(code=code, client_id=client_id)
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
    # Explicitly declare parsers so DRF parses the JSON body on DELETE too
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def delete(self, request):
        client_id, err = _require_client_id(request)
        if err:
            return err
        count, _ = AccMaster.objects.filter(client_id=client_id).delete()
        return Response({'deleted': count, 'client_id': client_id, 'table': 'acc_master_sync'})


# ── Misel (Firm Info) ─────────────────────────────────────

class MiselListView(APIView):
    def get(self, request):
        client_id, err = _require_client_id(request)
        if err:
            return err
        qs = Misel.objects.filter(client_id=client_id)
        serializer = MiselSerializer(qs, many=True)
        return Response(serializer.data)


class MiselBulkView(APIView):
    def post(self, request):
        serializer = BulkMiselSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)


class MiselTruncateView(APIView):
    # Explicitly declare parsers so DRF parses the JSON body on DELETE too
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def delete(self, request):
        client_id, err = _require_client_id(request)
        if err:
            return err
        count, _ = Misel.objects.filter(client_id=client_id).delete()
        return Response({'deleted': count, 'client_id': client_id, 'table': 'misel_sync'})


# ── AccInvMast (Invoices) ─────────────────────────────────

class AccInvMastListView(APIView):
    def get(self, request):
        client_id, err = _require_client_id(request)
        if err:
            return err
        customerid = request.query_params.get('customerid')
        qs = AccInvMast.objects.filter(client_id=client_id)
        if customerid:
            qs = qs.filter(customerid=customerid)
        serializer = AccInvMastSerializer(qs, many=True)
        return Response(serializer.data)


class AccInvMastDetailView(APIView):
    def get(self, request, slno):
        client_id, err = _require_client_id(request)
        if err:
            return err
        try:
            # FIX: scope by both slno AND client_id (slno is not globally unique)
            obj = AccInvMast.objects.get(slno=slno, client_id=client_id)
        except AccInvMast.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AccInvMastSerializer(obj).data)


class AccInvMastBulkView(APIView):
    def post(self, request):
        serializer = BulkAccInvMastSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)


class AccInvMastTruncateView(APIView):
    def delete(self, request):
        client_id, err = _require_client_id(request)
        if err:
            return err
        count, _ = AccInvMast.objects.filter(client_id=client_id).delete()
        return Response({'deleted': count, 'client_id': client_id, 'table': 'acc_invmast_sync'})


class AccInvMastSummaryView(APIView):
    def get(self, request):
        client_id, err = _require_client_id(request)
        if err:
            return err
        customerid = request.query_params.get('customerid')
        qs = AccInvMast.objects.filter(client_id=client_id)

        if customerid:
            qs = qs.filter(customerid=customerid)
            agg = qs.aggregate(
                total_sales=Sum('nettotal'),
                invoice_count=Count('slno'),
            )
            return Response({
                'customerid':    customerid,
                'client_id':     client_id,
                'total_sales':   agg['total_sales'] or 0,
                'invoice_count': agg['invoice_count'] or 0,
            })

        # All-customers summary for this client
        summary = qs.aggregate(
            total_invoices=Count('slno'),
            total_amount=Sum('nettotal'),
        )
        summary['client_id'] = client_id
        return Response(summary)