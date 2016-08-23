# vRouter App

## Configure vRouter App in ONOS
`curl -H "Content-Type: application/json" -X POST -d '{"controlPlaneConnectPoint":"of:001/1", "ospfEnabled": "true", "interfaces": ["b1-1"]}' --user onos:rocks http://onos-fabric:8181/onos/v1/network/configuration/apps/org.onosproject.router/router/`

## Delete vRotuer App config
`curl -X DELETE --user onos:rocks http://onos-fabric:8181/onos/v1/network/configuration/apps/org.onosproject.router/router/`

## Check vRotuer App config
`curl --user onos:rocks http://onos-fabric:8181/onos/v1/network/configuration/apps/org.onosproject.router/router/`

## Add Port
`curl --user onos:rocks -H "Content-Type: application/json" -X POST -d {"of:000000000001/1": {"interfaces": [{"ips": ["10.0.4.2/24"], "mac": "00:00:00:00:00:01", "vlan": "100", "name": "b1-1"}]}} http://onos-fabric:8181/onos/v1/network/configuration/ports/`