from django.db import models
from django.contrib.auth.models import User
#
from django.db import models

from geopy.geocoders import Nominatim

class Organisation(models.Model):
    org_id = models.AutoField(primary_key=True, db_column='org_id')
    org_name = models.CharField(max_length=255, db_column='org_name')
    org_type = models.CharField(max_length=255, db_column='org_type')
    org_phno = models.CharField(max_length=255, db_column='org_phno')
    org_email = models.CharField(max_length=255, db_column='org_email')
    org_loc = models.CharField(max_length=255, db_column='org_loc')
    org_coords = models.CharField(max_length=255, db_column='org_coords', blank=True, null=True)  # New column

    class Meta:
        db_table = 'organisation'

    def save(self, *args, **kwargs):
        if not self.org_coords:
            geolocator = Nominatim(user_agent="care")
            location = geolocator.geocode(self.org_loc)
            if location:
                self.org_coords = f"{location.latitude}, {location.longitude}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.org_name



class Benefactor(models.Model):
    ben_id = models.AutoField(primary_key=True, db_column='ben_id')
    ben_name = models.CharField(max_length=255, db_column='ben_name')
    ben_phno = models.CharField(max_length=255, db_column='ben_phno')
    ben_email = models.CharField(max_length=255, db_column='ben_email')
    ben_pref = models.CharField(max_length=255, db_column='ben_pref')
    org = models.ForeignKey(Organisation, on_delete=models.CASCADE, db_column='org_id')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user')
    class Meta:
        db_table = 'benefactor'

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            if self.org.org_coords:
                coords = self.org.org_coords.split(', ')
                if len(coords) == 2:
                    self.latitude = float(coords[0])
                    self.longitude = float(coords[1])
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ben_name



class Supply(models.Model):
    # Choices for supply_category
    SUPPLY_CATEGORY_CHOICES = [
    ('Medications', 'Medications'),
    ('Bandages & Dressings', 'Bandages & Dressings'),
    ('Diagnostic Equipment', 'Diagnostic Equipment'),
    ('Surgical Instruments', 'Surgical Instruments'),
    ('Patient Care', 'Patient Care'),
    ('Emergency Supplies', 'Emergency Supplies'),
    ('IV Supplies', 'IV Supplies'),
    ('Personal Protective Equipment', 'Personal Protective Equipment'),
    # Add other medical categories as needed
]

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    supply_id = models.AutoField(primary_key=True, db_column='supply_id')
    supply_type = models.CharField(max_length=255, db_column='supply_type')
    supply_category = models.CharField(max_length=255, choices=SUPPLY_CATEGORY_CHOICES, db_column='supply_category')    
    supply_quantity = models.IntegerField(db_column='supply_quantity')
    supply_unit = models.CharField(max_length=255, db_column='supply_unit')
    expiration_date = models.DateField(db_column='expiration_date')
    supply_descr = models.CharField(max_length=255, db_column='supply_descr')
    supply_condition = models.CharField(max_length=255, db_column='supply_condition')

    class Meta:
        db_table = 'supply'

    def __str__(self):
        return self.supply_type


class Donation(models.Model):
    donation_id = models.AutoField(primary_key=True, db_column='donation_id')
    donor = models.ForeignKey(Benefactor, on_delete=models.CASCADE, db_column='donor_id')
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE, db_column='supply_id')
    quantity_donated = models.CharField(max_length=255, db_column='quantity_donated')
    donation_date = models.DateField(db_column='donation_date')

    class Meta:
        db_table = 'donation'

    def __str__(self):
        return f"Donation {self.donation_id}"


class Notification(models.Model):
    notif_id = models.AutoField(primary_key=True, db_column='notif_id')
    ben = models.ForeignKey(Benefactor, on_delete=models.CASCADE, db_column='ben_id')
    notif_type = models.CharField(max_length=255, db_column='notif_type')
    message = models.CharField(max_length=255, db_column='message')
    timestamp = models.DateTimeField(db_column='timestamp')
    is_read = models.CharField(max_length=255, db_column='is_read')

    class Meta:
        db_table = 'notification'

    def __str__(self) :
        return f"Notification {self.notif_type}"

class Request(models.Model):
    req_id = models.AutoField(primary_key=True, db_column='req_id')
    rec = models.ForeignKey(Benefactor, on_delete=models.CASCADE, db_column='rec_id')
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE, db_column='supply_id')
    quantity_req = models.CharField(max_length=255, db_column='quantity_req')
    req_date = models.DateField(db_column='req_date')
    status = models.CharField(max_length=255, db_column='status')
    priority = models.CharField(max_length=255, db_column='priority')
    comments = models.CharField(max_length=255, db_column='comments')
    reason = models.CharField(max_length=255, db_column='reason')
    dest_loc = models.CharField(max_length=255, db_column='dest_loc')

    class Meta:
        db_table = 'request'

    def __str__(self):
        return f"Request {self.req_id}"


class SupplyShipment(models.Model):
    shipment_id = models.AutoField(primary_key=True, db_column='shipment_id')
    req = models.ForeignKey(Request, on_delete=models.CASCADE, db_column='req_id')
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE, db_column='supply_id')
    quantity_shipped = models.CharField(max_length=255, db_column='quantity_shipped')
    shipment_date = models.DateField(db_column='shipment_date')
    expected_delivery = models.DateField(db_column='expected_delivery')
    actual_delivery = models.DateField(db_column='actual_delivery')
    delivery_status = models.CharField(max_length=255, db_column='delivery_status')
    tracking_no = models.IntegerField(db_column='tracking_no')
    delivery_comments = models.CharField(max_length=255, db_column='delivery_comments')

    class Meta:
        db_table = 'supply_shipment'

    def __str__(self) -> str:
        return str(self.shipment_id)  # Convert shipment_id to string


class SupplyTrans(models.Model):
    trans_id = models.AutoField(primary_key=True, db_column='trans_id')
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE, db_column='supply_id')
    ben = models.ForeignKey(Benefactor, on_delete=models.CASCADE, db_column='ben_id')
    trans_type = models.CharField(max_length=255, db_column='trans_type')
    trans_quantity = models.CharField(max_length=255, db_column='trans_quantity')
    trans_date = models.DateField(db_column='trans_date')
    trans_comments = models.CharField(max_length=255, db_column='trans_comments')

    class Meta:
        db_table = 'supply_trans'  

    def __str__(self) -> str:
        return str(self.trans_id)


class IDProof(models.Model):
    PROOF_TYPE_CHOICES = [
        ('Aadhar', 'Aadhar'),
        ('Hospital ID', 'Hospital ID'),
        ('Organisation ID', 'Organisation ID'),
        # Add other choices here if needed
    ]
    
    id_proof_id = models.AutoField(primary_key=True, db_column='id_proof_id')
    benefactor = models.ForeignKey(Benefactor, on_delete=models.CASCADE, db_column='benefactor_id')
    proof_type = models.CharField(max_length=255, db_column='proof_type', choices=PROOF_TYPE_CHOICES)
    proof_number = models.CharField(max_length=255, db_column='proof_number')
    issue_date = models.DateField(db_column='issue_date', null=True, blank=True)
    expiry_date = models.DateField(db_column='expiry_date', null=True, blank=True)
    proof_document = models.FileField(upload_to='id_proofs/', db_column='proof_document')

    class Meta:
        db_table = 'id_proof'

    def __str__(self):
        return f"{self.proof_type} - {self.proof_number}"