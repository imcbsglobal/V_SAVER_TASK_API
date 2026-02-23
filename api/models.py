from django.db import models


class AccMaster(models.Model):
    code         = models.CharField(max_length=30, primary_key=True)
    name         = models.CharField(max_length=250)
    place        = models.CharField(max_length=60,  null=True, blank=True)
    exregnodate  = models.CharField(max_length=30,  null=True, blank=True)
    super_code   = models.CharField(max_length=5,   null=True, blank=True)
    phone2       = models.CharField(max_length=60,  null=True, blank=True)
    client_id    = models.CharField(max_length=50,  null=True, blank=True, db_index=True)
    synced_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'acc_master_sync'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Misel(models.Model):
    firm_name    = models.CharField(max_length=150, null=True, blank=True)
    address1     = models.CharField(max_length=50,  null=True, blank=True)
    client_id    = models.CharField(max_length=50,  null=True, blank=True, db_index=True)
    synced_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'misel_sync'

    def __str__(self):
        return f"{self.firm_name} - {self.address1}"


class AccInvMast(models.Model):
    slno         = models.BigIntegerField(primary_key=True)
    invdate      = models.DateField(null=True, blank=True)
    customerid   = models.CharField(max_length=30, null=True, blank=True)
    nettotal     = models.DecimalField(max_digits=16, decimal_places=3, null=True, blank=True)
    client_id    = models.CharField(max_length=50,  null=True, blank=True, db_index=True)
    synced_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'acc_invmast_sync'
        ordering = ['-invdate', '-slno']

    def __str__(self):
        return f"Invoice {self.slno} | {self.customerid} | {self.invdate} | {self.nettotal}"