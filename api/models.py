from django.db import models


class AccMaster(models.Model):
    code         = models.CharField(max_length=30)
    name         = models.CharField(max_length=250)
    place        = models.CharField(max_length=60,  null=True, blank=True)
    exregnodate  = models.CharField(max_length=30,  null=True, blank=True)
    super_code   = models.CharField(max_length=5,   null=True, blank=True)
    phone2       = models.CharField(max_length=60,  null=True, blank=True)
    client_id    = models.CharField(max_length=50,  db_index=True)   # NON-NULLABLE
    synced_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'acc_master_sync'
        ordering        = ['code']
        unique_together = [('code', 'client_id')]

    def __str__(self):
        return f"{self.code} - {self.name} [{self.client_id}]"


class Misel(models.Model):
    firm_name    = models.CharField(max_length=150, null=True, blank=True)
    address1     = models.CharField(max_length=50,  null=True, blank=True)
    client_id    = models.CharField(max_length=50,  db_index=True)   # NON-NULLABLE
    synced_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'misel_sync'
        unique_together = [('firm_name', 'client_id')]

    def __str__(self):
        return f"{self.firm_name} [{self.client_id}]"


class AccInvMast(models.Model):
    slno         = models.BigIntegerField()
    invdate      = models.DateField(null=True, blank=True)
    customerid   = models.CharField(max_length=30, null=True, blank=True)
    nettotal     = models.DecimalField(max_digits=16, decimal_places=3, null=True, blank=True)
    client_id    = models.CharField(max_length=50,  db_index=True)   # NON-NULLABLE
    synced_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'acc_invmast_sync'
        ordering        = ['-invdate', '-slno']
        unique_together = [('slno', 'client_id')]

    def __str__(self):
        return f"Invoice {self.slno} | {self.customerid} | {self.client_id}"