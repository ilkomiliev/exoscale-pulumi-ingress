import pulumi
import pulumiverse_exoscale as exoscale

cfg = pulumi.Config()
node_ports_world_accessible = cfg.get_bool("nodePortsWorldAccessible", True)
print(f"node_ports_world_accessible: {node_ports_world_accessible}")

cluster = exoscale.SKSCluster(
    resource_name="cluster01",
    zone="at-vie-1",
    name="cluster01",
    service_level="starter"
)

pulumi.export("endpoint", cluster.endpoint)
pulumi.export("state", cluster.state)

sks_security_grp = exoscale.SecurityGroup(resource_name="sks-security-group")

if node_ports_world_accessible:
    sg_rule_nodeport_services = exoscale.SecurityGroupRule(
        resource_name="sg-rule-nodeport-services",
        description="NodePort services",
        security_group_id=sks_security_grp.id,
        type="INGRESS",
        protocol="TCP",
        cidr="0.0.0.0/0",
        start_port=30000,
        end_port=32767
    )

sg_rule_sks_kubelet = exoscale.SecurityGroupRule(
    resource_name="sg-rule-sks-kubelet",
    description="SKS kubelet",
    security_group_id=sks_security_grp.id,
    type="INGRESS",
    protocol="TCP",
    start_port=10250,
    end_port=10250,
    user_security_group_id=sks_security_grp.id
)

sg_rule_calico_traffic = exoscale.SecurityGroupRule(
    resource_name="sg-rule-calico-traffic",
    description="Calico traffic",
    security_group_id=sks_security_grp.id,
    type="INGRESS",
    protocol="UDP",
    start_port=4789,
    end_port=4789,
    user_security_group_id=sks_security_grp.id
)

nodepool = exoscale.SKSNodepool(
    resource_name="nodepool01",
    cluster_id=cluster.id,
    size=2,
    zone="at-vie-1",
    instance_type="standard.medium",
    security_group_ids=[sks_security_grp.id],
    disk_size=60
)
