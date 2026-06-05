# VPC Integration Guide

## Overview
This document describes how CTyun VPC integrates with other CTyun services and external systems.

## Service Integration Matrix

| Service | Integration Type | Key Considerations |
|---|---|---|
| **ECS (Elastic Compute Service)** | Direct | Instances launch into subnets; Security Groups control access |
| **ELB (Elastic Load Balancer)** | Direct | Requires subnets in multiple AZs; Internet-facing vs internal |
| **RDS (Relational Database Service)** | Direct | Deploys into subnets; uses Security Groups; Multi-AZ across subnets |
| **Redis** | Direct | Deploys into subnets; uses Security Groups for access control |
| **OOS (Object-Oriented Storage)** | VPC Endpoint | Private connectivity via VPC Endpoint; no internet egress |
| **KMS (Key Management Service)** | VPC Endpoint | Private encryption key access; reduced latency |
| **Cloud Monitor** | API + Metrics | VPC metrics collection; alarm integration |
| **Cloud Audit** | API + Logs | VPC operation auditing; CloudTrail integration |
| **VPN Gateway** | Direct | Site-to-site VPN; customer gateway configuration |
| **Direct Connect** | Direct | Dedicated network connection; virtual interface to VPC |

## ECS Integration

### Launching Instances in VPC

```python
def launch_ecs_in_vpc(ecs_client, vpc_id, subnet_id, security_group_ids):
    """
    Launch ECS instance in VPC subnet with security groups.
    
    Args:
        ecs_client: ECS client instance
        vpc_id: VPC ID
        subnet_id: Subnet ID
        security_group_ids: List of security group IDs
    
    Returns:
        dict: Instance creation response
    """
    try:
        response = ecs_client.create_instances(
            instance_type='s6.medium.2',
            image_id='ctyun-image-ubuntu-20.04',
            vpc_id=vpc_id,
            subnet_id=subnet_id,
            security_group_ids=security_group_ids,
            instance_name='web-server-01',
            key_pair_name='my-keypair',
            # Optional: assign public IP
            allocate_public_ip=True,
            # Optional: instance tags
            tags=[
                {'Key': 'Environment', 'Value': 'Production'},
                {'Key': 'Application', 'Value': 'WebServer'}
            ]
        )
        
        instance_id = response['InstanceId']
        print(f"Launched instance {instance_id} in VPC {vpc_id}, subnet {subnet_id}")
        return response
        
    except Exception as e:
        print(f"Failed to launch instance: {e}")
        raise
```

### Security Group Coordination

```python
def create_vpc_security_group(vpc_client, vpc_id, group_name, description):
    """
    Create security group in VPC.
    
    Args:
        vpc_client: VPC client instance
        vpc_id: VPC ID
        group_name: Security group name
        description: Security group description
    
    Returns:
        str: Security group ID
    """
    try:
        response = vpc_client.create_security_group(
            vpc_id=vpc_id,
            group_name=group_name,
            description=description
        )
        
        group_id = response['GroupId']
        print(f"Created security group {group_id} in VPC {vpc_id}")
        return group_id
        
    except Exception as e:
        print(f"Failed to create security group: {e}")
        raise

def configure_web_security_group(vpc_client, group_id):
    """
    Configure security group for web servers.
    
    Args:
        vpc_client: VPC client instance
        group_id: Security group ID
    """
    rules = [
        # HTTP from anywhere
        {
            'ip_protocol': 'tcp',
            'from_port': 80,
            'to_port': 80,
            'cidr_ip': '0.0.0.0/0',
            'description': 'HTTP access'
        },
        # HTTPS from anywhere
        {
            'ip_protocol': 'tcp',
            'from_port': 443,
            'to_port': 443,
            'cidr_ip': '0.0.0.0/0',
            'description': 'HTTPS access'
        },
        # SSH from office IP
        {
            'ip_protocol': 'tcp',
            'from_port': 22,
            'to_port': 22,
            'cidr_ip': '203.0.113.0/24',
            'description': 'SSH from office'
        },
        # All traffic within VPC (for internal communication)
        {
            'ip_protocol': '-1',  # All protocols
            'from_port': -1,
            'to_port': -1,
            'cidr_ip': '10.0.0.0/16',  # VPC CIDR
            'description': 'Internal VPC traffic'
        }
    ]
    
    for rule in rules:
        try:
            vpc_client.authorize_security_group_ingress(
                group_id=group_id,
                ip_protocol=rule['ip_protocol'],
                from_port=rule['from_port'],
                to_port=rule['to_port'],
                cidr_ip=rule['cidr_ip'],
                description=rule['description']
            )
            print(f"Added rule: {rule['description']}")
        except Exception as e:
            print(f"Failed to add rule {rule['description']}: {e}")
```

## ELB Integration

### Creating Load Balancer in VPC

```python
def create_internal_elb(elb_client, vpc_id, subnet_ids, security_group_ids):
    """
    Create internal load balancer in VPC.
    
    Args:
        elb_client: ELB client instance
        vpc_id: VPC ID
        subnet_ids: List of subnet IDs (minimum 2 for HA)
        security_group_ids: List of security group IDs
    
    Returns:
        dict: Load balancer creation response
    """
    try:
        response = elb_client.create_load_balancer(
            name='internal-app-lb',
            vpc_id=vpc_id,
            subnet_ids=subnet_ids,
            security_group_ids=security_group_ids,
            scheme='internal',  # 'internal' or 'internet-facing'
            ip_address_type='ipv4',
            # Optional: tags
            tags=[
                {'Key': 'Environment', 'Value': 'Production'},
                {'Key': 'Application', 'Value': 'AppServer'}
            ]
        )
        
        lb_arn = response['LoadBalancerArn']
        dns_name = response['DNSName']
        print(f"Created internal load balancer {lb_arn} in VPC {vpc_id}")
        print(f"DNS name: {dns_name}")
        return response
        
    except Exception as e:
        print(f"Failed to create load balancer: {e}")
        raise
```

### Cross-Zone Load Balancing Considerations

```python
def validate_elb_subnets(vpc_client, subnet_ids):
    """
    Validate subnets for ELB deployment.
    
    Args:
        vpc_client: VPC client instance
        subnet_ids: List of subnet IDs
    
    Returns:
        dict: Validation results
    """
    results = {
        'valid': True,
        'issues': [],
        'subnet_details': []
    }
    
    try:
        subnets = vpc_client.describe_subnets(subnet_ids=subnet_ids)['Subnets']
        
        # Check minimum 2 subnets for HA
        if len(subnets) < 2:
            results['valid'] = False
            results['issues'].append(f"ELB requires at least 2 subnets, got {len(subnets)}")
        
        # Check they're in different AZs
        azs = set()
        for subnet in subnets:
            az = subnet['AvailabilityZone']
            azs.add(az)
            results['subnet_details'].append({
                'subnet_id': subnet['SubnetId'],
                'az': az,
                'cidr': subnet['CidrBlock'],
                'available_ips': subnet['AvailableIpAddressCount']
            })
        
        if len(azs) < 2:
            results['valid'] = False
            results['issues'].append(f"Subnets must be in different AZs, all in {azs}")
        
        # Check IP availability
        for detail in results['subnet_details']:
            if detail['available_ips'] < 8:  # ELB needs IPs for scaling
                results['valid'] = False
                results['issues'].append(
                    f"Subnet {detail['subnet_id']} has only {detail['available_ips']} "
                    f"available IPs (minimum 8 recommended for ELB)"
                )
        
        return results
        
    except Exception as e:
        results['valid'] = False
        results['issues'].append(f"Validation failed: {e}")
        return results
```

## RDS Integration

### Creating RDS Instance in VPC

```python
def create_rds_in_vpc(rds_client, vpc_id, subnet_group_name, security_group_ids):
    """
    Create RDS instance in VPC subnet group.
    
    Args:
        rds_client: RDS client instance
        vpc_id: VPC ID
        subnet_group_name: DB subnet group name
        security_group_ids: List of security group IDs
    
    Returns:
        dict: RDS creation response
    """
    try:
        # First create DB subnet group if it doesn't exist
        try:
            rds_client.describe_db_subnet_groups(db_subnet_group_name=subnet_group_name)
            print(f"DB subnet group {subnet_group_name} already exists")
        except:
            # Get subnets in VPC
            subnets = vpc_client.describe_subnets(
                filters=[{'name': 'vpc-id', 'values': [vpc_id]}]
            )['Subnets']
            
            # Select subnets for RDS (preferably private subnets)
            rds_subnets = []
            for subnet in subnets:
                # Simple heuristic: private subnets don't have 'public' in name
                if 'public' not in subnet.get('Name', '').lower():
                    rds_subnets.append(subnet['SubnetId'])
                    if len(rds_subnets) >= 2:  # Need at least 2 for Multi-AZ
                        break
            
            if len(rds_subnets) < 2:
                raise ValueError(f"Need at least 2 subnets for RDS, found {len(rds_subnets)}")
            
            rds_client.create_db_subnet_group(
                db_subnet_group_name=subnet_group_name,
                db_subnet_group_description=f"Subnet group for RDS in VPC {vpc_id}",
                subnet_ids=rds_subnets
            )
            print(f"Created DB subnet group {subnet_group_name}")
        
        # Create RDS instance
        response = rds_client.create_db_instance(
            db_instance_identifier='production-db',
            db_instance_class='db.m5.large',
            engine='mysql',
            engine_version='8.0',
            master_username='admin',
            master_user_password='{{env.DB_PASSWORD}}',  # From environment
            allocated_storage=100,
            db_subnet_group_name=subnet_group_name,
            vpc_security_group_ids=security_group_ids,
            multi_az=True,  # For high availability
            publicly_accessible=False,  # Keep private
            backup_retention_period=7,
            tags=[
                {'Key': 'Environment', 'Value': 'Production'},
                {'Key': 'Application', 'Value': 'Database'}
            ]
        )
        
        db_instance_id = response['DBInstance']['DBInstanceIdentifier']
        print(f"Creating RDS instance {db_instance_id} in VPC {vpc_id}")
        return response
        
    except Exception as e:
        print(f"Failed to create RDS instance: {e}")
        raise
```

## VPC Endpoints for Private Connectivity

### OOS VPC Endpoint

```python
def create_oos_vpc_endpoint(vpc_client, vpc_id, subnet_ids):
    """
    Create VPC endpoint for OOS (Object-Oriented Storage).
    
    Args:
        vpc_client: VPC client instance
        vpc_id: VPC ID
        subnet_ids: List of subnet IDs for endpoint
    
    Returns:
        dict: VPC endpoint creation response
    """
    try:
        response = vpc_client.create_vpc_endpoint(
            vpc_id=vpc_id,
            service_name='com.ctyun.cn.oos',  # OOS service name
            vpc_endpoint_type='Interface',
            subnet_ids=subnet_ids,
            # Optional: security groups for endpoint
            security_group_ids=['sg-12345678'],
            # Optional: private DNS
            private_dns_enabled=True,
            # Optional: tags
            tags=[
                {'Key': 'Service', 'Value': 'OOS'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        )
        
        endpoint_id = response['VpcEndpoint']['VpcEndpointId']
        print(f"Created OOS VPC endpoint {endpoint_id}")
        return response
        
    except Exception as e:
        print(f"Failed to create VPC endpoint: {e}")
        raise
```

### KMS VPC Endpoint

```python
def create_kms_vpc_endpoint(vpc_client, vpc_id, subnet_ids):
    """
    Create VPC endpoint for KMS (Key Management Service).
    
    Args:
        vpc_client: VPC client instance
        vpc_id: VPC ID
        subnet_ids: List of subnet IDs for endpoint
    
    Returns:
        dict: VPC endpoint creation response
    """
    try:
        response = vpc_client.create_vpc_endpoint(
            vpc_id=vpc_id,
            service_name='com.ctyun.cn.kms',  # KMS service name
            vpc_endpoint_type='Interface',
            subnet_ids=subnet_ids,
            security_group_ids=['sg-12345678'],
            private_dns_enabled=True,
            tags=[
                {'Key': 'Service', 'Value': 'KMS'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        )
        
        endpoint_id = response['VpcEndpoint']['VpcEndpointId']
        print(f"Created KMS VPC endpoint {endpoint_id}")
        
        # Update route tables to use endpoint
        route_tables = vpc_client.describe_route_tables(
            filters=[{'name': 'vpc-id', 'values': [vpc_id]}]
        )['RouteTables']
        
        for rt in route_tables:
            rt_id = rt['RouteTableId']
            # Add route for KMS via endpoint
            vpc_client.create_route(
                route_table_id=rt_id,
                destination_cidr_block='kms.ctyun.cn',  # KMS service endpoint
                vpc_endpoint_id=endpoint_id
            )
            print(f"Added KMS route to route table {rt_id}")
        
        return response
        
    except Exception as e:
        print(f"Failed to create KMS VPC endpoint: {e}")
        raise
```

## VPN Gateway Integration

### Site-to-Site VPN

```python
def create_vpn_connection(vpc_client, vpc_id, customer_gateway_id):
    """
    Create VPN connection to on-premises network.
    
    Args:
        vpc_client: VPC client instance
        vpc_id: VPC ID
        customer_gateway_id: Customer Gateway ID
    
    Returns:
        dict: VPN connection response
    """
    try:
        # Create Virtual Private Gateway
        vpg_response = vpc_client.create_vpn_gateway(
            type='ipsec.1',
            tags=[
                {'Key': 'Name', 'Value': 'OnPrem-VPN'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        )
        vpg_id = vpg_response['VpnGateway']['VpnGatewayId']
        
        # Attach to VPC
        vpc_client.attach_vpn_gateway(
            vpc_id=vpc_id,
            vpn_gateway_id=vpg_id
        )
        
        # Create VPN connection
        response = vpc_client.create_vpn_connection(
            customer_gateway_id=customer_gateway_id,
            vpn_gateway_id=vpg_id,
            type='ipsec.1',
            static_routes_only=True,
            # Optional: custom tunnel options
            options={
                'TunnelOptions': [
                    {
                        'TunnelInsideCidr': '169.254.10.0/30',
                        'PreSharedKey': '{{env.VPN_PSK}}'  # From environment
                    }
                ]
            },
            tags=[
                {'Key': 'Connection', 'Value': 'OnPrem-VPN'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        )
        
        vpn_id = response['VpnConnection']['VpnConnectionId']
        print(f"Created VPN connection {vpn_id} for VPC {vpc_id}")
        
        # Add static routes for on-premises networks
        on_prem_cidrs = ['10.1.0.0/16', '10.2.0.0/16']  # Example on-prem CIDRs
        for cidr in on_prem_cidrs:
            vpc_client.create_vpn_connection_route(
                vpn_connection_id=vpn_id,
                destination_cidr_block=cidr
            )
            print(f"Added route to on-premises network {cidr}")
        
        return response
        
    except Exception as e:
        print(f"Failed to create VPN connection: {e}")
        raise
```

## Cloud Monitor Integration

### VPC Monitoring Dashboard

```python
def setup_vpc_monitoring_dashboard(monitor_client, vpc_id):
    """
    Set up Cloud Monitor dashboard for VPC.
    
    Args:
        monitor_client: Cloud Monitor client
        vpc_id: VPC ID to monitor
    """
    dashboard_config = {
        'dashboardName': f'vpc-{vpc_id}-dashboard',
        'dashboardBody': json.dumps({
            'widgets': [
                {
                    'type': 'metric',
                    'properties': {
                        'metrics': [
                            ['CTyun/VPC', 'NetworkInBytes', 'VpcId