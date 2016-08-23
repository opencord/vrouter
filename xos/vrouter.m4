tosca_definitions_version: tosca_simple_yaml_1_0

# compile this with "m4 vrouter.m4 > vrouter.yaml"

# include macros
include(macros.m4)

node_types:
    
    tosca.nodes.VRouterService:
        derived_from: tosca.nodes.Root
        description: >
            CORD: The vRouter Service.
        capabilities:
            xos_base_service_caps
        properties:
            xos_base_props
            xos_base_service_props
            rest_hostname:
                type: string
                required: false
            rest_port:
                type: string
                required: false
            rest_user:
                type: string
                required: false
            rest_pass:
                type: string
                required: false

    tosca.nodes.VRouterDevice:
        derived_from: tosca.nodes.Root
        description: >
            CORD: The vRouter Device.
        capabilities:
            xos_base_service_caps
        properties:
            xos_base_props
            openflow_id:
                type: string
                required: true
            config_key:
                type: string
                required: false
            driver:
                type: string
                required: true

    tosca.nodes.VRouterPort:
        derived_from: tosca.nodes.Root
        description: >
            CORD: The vRouter Port.
        capabilities:
            xos_base_service_caps
        properties:
            xos_base_props
            openflow_id:
                type: string
                required: true

    tosca.nodes.VRouterInterface:
        derived_from: tosca.nodes.Root
        description: >
            CORD: The vRouter Interface.
        capabilities:
            xos_base_service_caps
        properties:
            xos_base_props
            name:
                type: string
                required: true
            mac:
                type: string
                required: true
            vlan:
                type: string
                required: false

    tosca.nodes.VRouterIp:
        derived_from: tosca.nodes.Root
        description: >
            CORD: The vRouter Ip.
        capabilities:
            xos_base_service_caps
        properties:
            xos_base_props
            ip:
                type: string
                required: true

    tosca.nodes.VRouterApp:
        derived_from: tosca.nodes.Root
        description: >
            CORD: The vRouter ONOS App Config.
        capabilities:
            xos_base_service_caps
        properties:
            xos_base_props
            name:
                type: string
                required: true
            control_plane_connect_point:
                type: string
                required: true
            ospf_enabled:
                type: boolean
                required: true

    tosca.relationships.PortOfDevice:
            derived_from: tosca.relationships.Root
            valid_target_types: [ tosca.capabilities.xos.VRouterPort ]

    tosca.relationships.InterfaceOfPort:
            derived_from: tosca.relationships.Root
            valid_target_types: [ tosca.capabilities.xos.VRouterInterface ]

    tosca.relationships.IpOfInterface:
            derived_from: tosca.relationships.Root
            valid_target_types: [ tosca.capabilities.xos.VRouterIp ]