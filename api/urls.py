from django.urls import path
from .views import (
    HealthView,
    AccMasterListView, AccMasterDetailView, AccMasterBulkView, AccMasterTruncateView,
    MiselListView, MiselBulkView, MiselTruncateView,
    AccInvMastListView, AccInvMastDetailView, AccInvMastBulkView,
    AccInvMastSummaryView, AccInvMastTruncateView,
)

urlpatterns = [

    # ── Health ────────────────────────────────────────────
    path('vsaver/status/',          HealthView.as_view(),              name='vsaver-status'),

    # ── Debtors ───────────────────────────────────────────
    path('debtors/',                AccMasterListView.as_view(),       name='debtor-list'),
    path('debtors/bulk/',           AccMasterBulkView.as_view(),       name='debtor-bulk'),
    path('debtors/truncate/',       AccMasterTruncateView.as_view(),   name='debtor-truncate'),
    path('debtors/<str:code>/',     AccMasterDetailView.as_view(),     name='debtor-detail'),

    # ── Firm info ─────────────────────────────────────────
    path('misel/',                  MiselListView.as_view(),           name='misel-list'),
    path('misel/bulk/',             MiselBulkView.as_view(),           name='misel-bulk'),
    path('misel/truncate/',         MiselTruncateView.as_view(),       name='misel-truncate'),

    # ── Invoices ──────────────────────────────────────────
    path('invoices/',               AccInvMastListView.as_view(),      name='invoice-list'),
    path('invoices/bulk/',          AccInvMastBulkView.as_view(),      name='invoice-bulk'),
    path('invoices/summary/',       AccInvMastSummaryView.as_view(),   name='invoice-summary'),
    path('invoices/truncate/',      AccInvMastTruncateView.as_view(),  name='invoice-truncate'),
    path('invoices/<int:slno>/',    AccInvMastDetailView.as_view(),    name='invoice-detail'),
]