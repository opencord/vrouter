# vRouter service

The vRouter Service is responsible for configuring routes in the Trellis Fabric.

It is required that the `vRouter` service is a `provider_service`
of the `fabric` service, and the `fabric` service is a `provider_service` of
 `onos` service (containing the correct applications),
so that this will be part of your service graph:

```text
ONOS_Fabric <- Fabric <- vRouter
```

## Models

The `vRouter`service is composed of the following models:

- `VRouterService`. Extends the core `Service` model, has no additional vRouter-specific fields.
- `VRouterServiceInstance`. Extends the core `ServiceInstance` model, has no additional vRouter-specific fields.
- `VRouterStaticRoute` implements a static route.
    - `vrouter`. Relation to the `VRouterService` that owns this route.
    - `prefix`. The destination prefix and netmask (IP/NM).
    - `next_hop`. The next-hop for this route.

## Example TOSCA: Configure a static route

This is an example recipe to configure a static route so that your
Subscribers can get Internet access:

```yaml
tosca_definitions_version: tosca_simple_yaml_1_0
imports:
  - custom_types/vrouterserviceinstance.yaml
  - custom_types/vrouterstaticroute.yaml
description: Creates a vrouter and pushes a static route
topology_template:
  node_templates:
    vrouter#my_vrouter:
      type: tosca.nodes.VRouterServiceInstance
      properties:
        name: my_vrouter

    # Add a static route to the vRouter
    route#my_route:
      type: tosca.nodes.VRouterStaticRoute
      properties:
        prefix: "0.0.0.0/0" # The destination prefix and netmask (xxx.yyy.www.zzz/nm)
        next_hop: "192.168.0.254" # The next-hop for the route
      requirements:
        - vrouter:
            node: vrouter#my_vrouter
            relationship: tosca.relationships.BelongsToOne
```

## Integration with other Services

The `vRouter` service depends upon the `Fabric` service.

## Synchronizer Workflows

### SyncRoutes

The `SyncRoutes` step synchronizes `VRouterStaticRoute` objects to ONOS.
