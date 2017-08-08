
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.contrib import admin

from services.vrouter.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.models import AddressPool
from core.admin import ServiceAppAdmin, SliceInline, ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline, ServicePrivilegeInline, AddressPoolInline, SubscriberLinkInline, ProviderLinkInline, ProviderDependencyInline,SubscriberDependencyInline
from core.middleware import get_request

from functools import update_wrapper
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.utils import quote


class VRouterPortInline(XOSTabularInline):
    model = VRouterPort
    fields = ['openflow_id']
    suit_classes = 'suit-tab suit-tab-vrouter_ports'
    extra = 0


class VRouterInterfaceInline(XOSTabularInline):
    model = VRouterInterface
    fields = ['name', 'mac', 'vlan']
    suit_classes = 'suit-tab suit-tab-vrouter_interfaces'
    extra = 0


class VRouterIpInline(XOSTabularInline):
    model = VRouterIp
    fields = ['ip']
    suit_classes = 'suit-tab suit-tab-vrouter_ips'
    extra = 0


class VRouterServiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VRouterServiceForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        return super(VRouterServiceForm, self).save(commit=commit)

    class Meta:
        model = VRouterService
        fields = '__all__'


class VRouterServiceAdmin(ReadOnlyAwareAdmin):
    model = VRouterService
    verbose_name = "vRouter Service"
    verbose_name_plural = "vRouter Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {
        'fields': [
            'backend_status_text',
            'name',
            'enabled',
            'versionNumber',
            'description',
            'view_url',
            'icon_url',
            'rest_hostname',
            'rest_port',
            'rest_user',
            'rest_pass',
        ],
        'classes':['suit-tab suit-tab-general']})]

    # NOTE make rest_* params editable
    readonly_fields = (
        'backend_status_text',
        'rest_hostname',
        'rest_port',
        'rest_user',
        'rest_pass'
    )
    inlines = [SliceInline, ServiceAttrAsTabInline, ServicePrivilegeInline, AddressPoolInline, ProviderDependencyInline,SubscriberDependencyInline]
    form = VRouterServiceForm

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs = (
        ('general', 'vRouter Service Details'),
        ('administration', 'Administration'),
        ('addresspools', 'Addresses'),
        # ('tools', 'Tools'),
        ('slices', 'Slices'),
        ('serviceattrs', 'Additional Attributes'),
        ('servicetenants', 'Dependencies'),
        ('serviceprivileges', 'Privileges'),
    )

    suit_form_includes = ('vrouteradmin.html', 'top', 'administration')  # ('hpctools.html', 'top', 'tools') )

    def get_queryset(self, request):
        return VRouterService.select_by_user(request.user)


class VRouterTenantForm(forms.ModelForm):
    gateway_ip = forms.CharField(required=False)
    gateway_mac = forms.CharField(required=False)
    cidr = forms.CharField(required=False)

    def __init__(self,*args,**kwargs):
        super (VRouterTenantForm,self ).__init__(*args,**kwargs)
        self.fields['owner'].queryset = VRouterService.objects.all()
        if self.instance:
            # fields for the attributes
            self.fields['gateway_ip'].initial = self.instance.gateway_ip
            self.fields['gateway_mac'].initial = self.instance.gateway_mac
            self.fields['cidr'].initial = self.instance.cidr
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            if VRouterService.objects.exists():
               self.fields["owner"].initial = VRouterService.objects.first()

    def save(self, commit=True):
        return super(VRouterTenantForm, self).save(commit=commit)

    class Meta:
        model = VRouterTenant
        fields = '__all__'


class VRouterTenantAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', 'public_ip')
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [(None, {
        'fields': [
            'backend_status_text', 'owner',
            'address_pool', 'public_ip', 'public_mac', 'gateway_ip', 'gateway_mac', 'cidr'],
        'classes':['suit-tab suit-tab-general']
    })]
    readonly_fields = ('backend_status_text', 'service_specific_attribute', 'gateway_ip', 'gateway_mac', 'cidr')
    inlines = (ProviderLinkInline, SubscriberLinkInline)
    form = VRouterTenantForm

    suit_form_tabs = (('general', 'Details'), ('servicelinks','Links'),)

    def get_queryset(self, request):
        return VRouterTenant.select_by_user(request.user)


class VRouterDeviceAdmin(ReadOnlyAwareAdmin):
    list_display = ('name', 'openflow_id', 'config_key', 'driver')
    fieldsets = [(None, {
        'fields': ['name', 'openflow_id', 'vrouter_service', 'config_key', 'driver'],
        'classes':['suit-tab suit-tab-general']
    })]
    inlines = [VRouterPortInline]

    suit_form_tabs = (
        ('general', 'Device Details'),
        ('vrouter_ports', 'Ports'),
    )


class VRouterPortAdmin(ReadOnlyAwareAdmin):
    list_display = ('name', 'openflow_id', 'vrouter_device')
    fieldsets = [(None, {
        'fields': ['name', 'openflow_id', 'vrouter_service', 'vrouter_device'],
        'classes':['suit-tab suit-tab-general']
    })]
    inlines = [VRouterInterfaceInline]

    suit_form_tabs = (
        ('general', 'Ports Details'),
        ('vrouter_interfaces', 'Interfaces'),
    )


class VRouterInterfaceAdmin(ReadOnlyAwareAdmin):
    list_display = ('name', 'mac', 'vlan')
    fieldsets = [(None, {
        'fields': ['name', 'vrouter_port', 'mac', 'vlan'],
        'classes':['suit-tab suit-tab-general']
    })]
    inlines = [VRouterIpInline]

    suit_form_tabs = (
        ('general', 'Interfaces Details'),
        ('vrouter_ips', 'Ips'),
    )


class VRouterIpAdmin(ReadOnlyAwareAdmin):
    list_display = ('name', 'ip', 'vrouter_interface')
    fieldsets = [(None, {'fields': ['name', 'ip', 'vrouter_interface']})]


class VRouterAppAdmin(ReadOnlyAwareAdmin):
    list_display = ('name', 'control_plane_connect_point', 'ospf_enabled')
    fieldsets = [(None, {'fields': ['name', 'vrouter_service', 'control_plane_connect_point', 'ospf_enabled']})]


admin.site.register(VRouterService, VRouterServiceAdmin)
admin.site.register(VRouterTenant, VRouterTenantAdmin)
admin.site.register(VRouterDevice, VRouterDeviceAdmin)
admin.site.register(VRouterPort, VRouterPortAdmin)
admin.site.register(VRouterInterface, VRouterInterfaceAdmin)
admin.site.register(VRouterIp, VRouterIpAdmin)
admin.site.register(VRouterApp, VRouterAppAdmin)

