from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

class InterfaceNames(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=False)
    abbrev = models.CharField(max_length=100, blank=True, default='')
    updated_on = models.DateTimeField(auto_now_add=False)

class InterfaceData(models.Model):
    device_id = models.ForeignKey(Device, on_delete=models.CASCADE)

class StackData(models.Model):
    interface_name_id =
    model = models.CharField(max_length=100, blank=True, default='')
    os_version = models.CharField(max_length=100, blank=True, default='')
    shelves = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False)

class Serials(models.Model):
    serial_number = models.CharField(max_length=100, blank=True, default='')
    asset_tag = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False)

class OsVersions(models.Model):
    os_version = models.CharField(max_length=100, blank=True, default='')

class Models(models.Model):
    model =

class Vendors(models.Model):
    vendor =

class Device(models.Model):
    name = models.CharField(max_length=100, blank=True, default='')
    hostname = models.CharField(max_length=100, blank=True, default='')
    port = 
    user_id = 
    platform = 
    groups =
    data =
    connection_options =
    defaults =
    vendor_id =
    model_id =
    os_version_data = 
    serial_id =
    uptime =
    enabled =
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=False)