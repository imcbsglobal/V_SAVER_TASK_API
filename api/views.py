from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count

from .models import AccMaster, Misel, AccInvMast
from .serializers import (
    AccMasterSerializer, BulkAccMasterSerializer,
    MiselSerializer, BulkMiselSerializer,
    AccInvMastSerializer, BulkAccInvMastSerializer,
)


# ── Health ────────────────────────────────────────────────
class HealthView(APIView):
    def get(self, request):
        return Response({
            'status'            : 'ok',
            'project'           : 'V-Saver API',
            'acc_master_records': AccMaster.objects.count(),
            'misel_records'     : Misel.objects.count(),
            'invoice_records'   : AccInvMast.objects.count(),
        })


# ── AccMaster ─────────────────────────────────────────────
class AccMasterListView(APIView):
    def get(self, request):
        qs = AccMaster.objects.all()
        if s := request.query_params.get('search'): qs = qs.filter(name__icontains=s)
        if p := request.query_params.get('place'):  qs = qs.filter(place__icontains=p)
        if c := request.query_params.get('code'):   qs = qs.filter(code__icontains=c)
        return Response({'count': qs.count(), 'results': AccMasterSerializer(qs, many=True).data})

    def post(self, request):
        ser = AccMasterSerializer(data=request.data)
        if ser.is_valid():
            obj, created = AccMaster.objects.update_or_create(
                code=ser.validated_data['code'],
                defaults={k: v for k, v in ser.validated_data.items() if k != 'code'}
            )
            return Response(AccMasterSerializer(obj).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class AccMasterDetailView(APIView):
    def get(self, request, code):
        return Response(AccMasterSerializer(get_object_or_404(AccMaster, code=code)).data)

    def put(self, request, code):
        obj = get_object_or_404(AccMaster, code=code)
        ser = AccMasterSerializer(obj, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class AccMasterBulkView(APIView):
    def post(self, request):
        ser = BulkAccMasterSerializer(data=request.data)
        if ser.is_valid():
            return Response(ser.create(ser.validated_data))
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Misel ─────────────────────────────────────────────────
class MiselListView(APIView):
    def get(self, request):
        qs = Misel.objects.all()
        return Response({'count': qs.count(), 'results': MiselSerializer(qs, many=True).data})

    def post(self, request):
        ser = MiselSerializer(data=request.data)
        if ser.is_valid():
            obj, created = Misel.objects.update_or_create(
                firm_name=ser.validated_data.get('firm_name'),
                defaults={k: v for k, v in ser.validated_data.items() if k != 'firm_name'}
            )
            return Response(MiselSerializer(obj).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class MiselBulkView(APIView):
    def post(self, request):
        ser = BulkMiselSerializer(data=request.data)
        if ser.is_valid():
            return Response(ser.create(ser.validated_data))
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


# ── AccInvMast ────────────────────────────────────────────
class AccInvMastListView(APIView):
    """
    GET /api/invoices/
    GET /api/invoices/?customerid=XXX
    GET /api/invoices/?from=2024-01-01&to=2024-12-31
    GET /api/invoices/?search=name   (searches customerid)
    """
    def get(self, request):
        qs = AccInvMast.objects.all()
        if c := request.query_params.get('customerid'): qs = qs.filter(customerid__icontains=c)
        if s := request.query_params.get('search'):     qs = qs.filter(customerid__icontains=s)
        if f := request.query_params.get('from'):       qs = qs.filter(invdate__gte=f)
        if t := request.query_params.get('to'):         qs = qs.filter(invdate__lte=t)
        return Response({'count': qs.count(), 'results': AccInvMastSerializer(qs, many=True).data})

    def post(self, request):
        ser = AccInvMastSerializer(data=request.data)
        if ser.is_valid():
            obj, created = AccInvMast.objects.update_or_create(
                slno=ser.validated_data['slno'],
                defaults={k: v for k, v in ser.validated_data.items() if k != 'slno'}
            )
            return Response(AccInvMastSerializer(obj).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class AccInvMastDetailView(APIView):
    """GET /api/invoices/<slno>/"""
    def get(self, request, slno):
        return Response(AccInvMastSerializer(get_object_or_404(AccInvMast, slno=slno)).data)

    def put(self, request, slno):
        obj = get_object_or_404(AccInvMast, slno=slno)
        ser = AccInvMastSerializer(obj, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class AccInvMastBulkView(APIView):
    """POST /api/invoices/bulk/"""
    def post(self, request):
        ser = BulkAccInvMastSerializer(data=request.data)
        if ser.is_valid():
            return Response(ser.create(ser.validated_data))
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class AccInvMastSummaryView(APIView):
    """GET /api/invoices/summary/ — total sales per customer"""
    def get(self, request):
        data = (
            AccInvMast.objects
            .values('customerid')
            .annotate(total_sales=Sum('nettotal'), invoice_count=Count('slno'))
            .order_by('-total_sales')
        )
        return Response({'count': len(data), 'results': list(data)})