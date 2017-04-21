def _get_interfaces(self):
    app_interfaces = []
    devices = VRouterDevice.objects.filter(vrouter_service=self.vrouter_service)
    for device in devices:
        ports = VRouterPort.objects.filter(vrouter_device=device.id)
        for port in ports:
            interfaces = VRouterInterface.objects.filter(vrouter_port=port.id)
            for iface in interfaces:
                app_interfaces.append(iface.name)
    return app_interfaces

