from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *




@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('org_id', 'org_name', 'org_type', 'org_phno', 'org_email', 'org_loc','org_coords')

@admin.register(Benefactor)
class BenefactorAdmin(admin.ModelAdmin):
    list_display = ('ben_id', 'ben_name', 'ben_phno', 'ben_email', 'ben_pref', 'org', 'user','latitude','longitude')

@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('supply_id', 'supply_type', 'supply_category', 'supply_quantity', 'supply_unit', 'expiration_date', 'supply_descr', 'supply_condition','user')

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donation_id', 'donor_id', 'supply_id', 'quantity_donated', 'donation_date')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notif_id', 'ben_id', 'notif_type', 'message', 'timestamp', 'is_read')

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('req_id', 'rec_id', 'supply_id', 'quantity_req', 'req_date', 'status', 'priority', 'comments', 'reason', 'dest_loc')

@admin.register(SupplyShipment)
class SupplyShipmentAdmin(admin.ModelAdmin):
    list_display = ('shipment_id', 'req_id', 'supply_id', 'quantity_shipped', 'shipment_date', 'expected_delivery', 'actual_delivery', 'delivery_status', 'tracking_no', 'delivery_comments')
    search_fields = ('shipment_id', 'tracking_no')  # Add relevant fields here
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        print(queryset)  # Add this line to debug the queryset
        return queryset

@admin.register(SupplyTrans)
class SupplyTransAdmin(admin.ModelAdmin):
    list_display = ('trans_id', 'supply_id', 'ben_id', 'trans_type', 'trans_quantity', 'trans_date', 'trans_comments')


@admin.register(IDProof)
class IDProofAdmin(admin.ModelAdmin):
    list_display = ('id_proof_id', 'benefactor_id', 'proof_type', 'proof_number', 'issue_date', 'expiry_date','proof_document')
    search_fields = ('proof_type', 'proof_number', 'benefactor__ben_name')
    list_filter = ('proof_type', 'issue_date', 'expiry_date')