# CTyun VPC API & SDK Usage

## Overview
This document provides API and SDK usage examples for CTyun VPC operations. Since VPC is not supported by the CTyun CLI, all operations must use the SDK/API.

## SDK Installation and Setup

### Python SDK Installation
```bash
# Install CTyun Python SDK
pip install ctyun-sdk

# Or using uv
uv pip install ctyun-sdk
```

### SDK Client Initialization
```python
from ctyun_sdk import CtyunClient

# Initialize client with environment variables
client = CtyunClient(
    access_key='{{env.CTYUN_ACCESS_KEY}}',
    secret_key='{{env.CTYUN_SECRET_KEY}}',
    region='{{env.CTYUN_REGION}}',  # e.g., 'cn-gz'
    endpoint='vpc.ctyun.cn',  # VPC service endpoint
    scheme='https',
    timeout=30
)

# Alternatively, use config file
# ~/.ctyun/config format:
# [default]
# access_key = AKID...
# secret_key = SECRET...
# region_id = cn-gz
# endpoint = vpc.ctyun.cn
# scheme = https
# timeout = 20
```

## VPC Operations

### Create VPC
```python
def create_vpc(client, vpc_name, cidr_block, description=None):
    """
    Create a new VPC.
    
    Args:
        client: CtyunClient instance
        vpc_name: Name for the VPC
        cidr_block: CIDR block (e.g., '10.0.0.0/16')
        description: Optional description
    
    Returns:
        dict: VPC creation response
    """
    try:
        response = client.vpc.create_vpc(
            name=vpc_name,
            cidr_block=cidr_block,
            description=description or f"VPC {vpc_name}",
            # Optional: enable_dns_support=True,
            # Optional: enable_dns_hostnames=True,
            # Optional: tenancy='default'  # 'default' or 'dedicated'
        )
        
        vpc_id = response['Vpc']['VpcId']
        print(f"Created VPC: {vpc_id}")
        return response
        
    except Exception as e:
        print(f"Failed to create VPC: {e}")
        raise
```

### List VPCs
```python
def list_vpcs(client, vpc_ids=None, filters=None, max_results=100):
    """
    List VPCs in the region.
    
    Args:
        client: CtyunClient instance
        vpc_ids: Optional list of VPC IDs to filter
        filters: Optional list of filters
        max_results: Maximum number of results
    
    Returns:
        list: VPC objects
    """
    try:
        params = {'max_results': max_results}
        if vpc_ids:
            params['vpc_ids'] = vpc_ids
        if filters:
            params['filters'] = filters
            
        response = client.vpc.describe_vpcs(**params)
        vpcs = response.get('Vpcs', [])
        
        print(f"Found {len(vpcs)} VPC(s)")
        for vpc in vpcs:
            print(f"  - {vpc['VpcId']}: {vpc.get('Name', 'Unnamed')} "
                  f"({vpc['CidrBlock']}) - {vpc['State']}")
        
        return vpcs
        
    except Exception as e:
        print(f"Failed to list VPCs: {e}")
        raise
```

### Delete VPC
```python
def delete_vpc(client, vpc_id, force=False):
    """
    Delete a VPC after checking dependencies.
    
    Args:
        client: CtyunClient instance
        vpc_id: VPC ID to delete
        force: If True, skip dependency checks (DANGEROUS)
    
    Returns:
        bool: True if deletion successful
    """
    if not force:
        # Check for dependencies
        dependencies = check_vpc_dependencies(client, vpc_id)
        if dependencies:
            print(f"Cannot delete VPC {vpc_id}. Active dependencies:")
            for dep_type, dep_list in dependencies.items():
                if dep_list:
                    print(f"  {dep_type}: {', '.join(dep_list[:5])}")
                    if len(dep_list) > 5:
                        print(f"    ... and {len(dep_list) - 5} more")
            return False
    
    try:
        # SAFETY GATE: Require explicit confirmation
        print(f"WARNING: About to delete VPC {vpc_id}")
        confirmation = input("Type 'DELETE' to confirm: ")
        if confirmation != 'DELETE':
            print("Deletion cancelled")
            return False
            
        response = client.vpc.delete_vpc(vpc_id=vpc_id)
        request_id = response.get('RequestId')
        print(f"VPC deletion initiated. Request ID: {request_id}")
        
        # Wait for deletion to complete
        import time
        for i in range(30):  # Wait up to 5 minutes
            try:
                client.vpc.describe_vpcs(vpc_ids=[vpc_id])
                print(f"Waiting for VPC deletion... ({i * 10}s)")
                time.sleep(10)
            except Exception as e:
                if 'not found' in str(e).lower() or '404' in str(e):
                    print(f"VPC {vpc_id} successfully deleted")
                    return True
                else:
                    raise
        
        print(f"VPC {vpc_id} deletion timed out")
        return False
        
    except Exception as e:
        print(f"Failed to delete VPC: {e}")
        raise

def check_vpc_dependencies(client, vpc_id):
    """
    Check for resources that would block VPC deletion.
    
    Returns:
        dict: Dependency types and IDs
    """
    dependencies = {
        'subnets': [],
        'route_tables': [],
        'network_interfaces': [],
        'vpc_peering_connections': [],
        'internet_gateways': [],
        'nat_gateways': [],
        'vpc_endpoints': []
    }
    
    try:
        # Check subnets
        subnets = client.vpc.describe_subnets(
            filters=[{'name': 'vpc-id', 'values': [vpc_id]}]
        ).get('Subnets', [])
        dependencies['subnets'] = [s['SubnetId'] for s in subnets]
        
        # Check route tables (excluding default)
        route_tables = client.vpc.describe_route_tables(
            filters=[{'name': 'vpc-id', 'values': [vpc_id]}]
        ).get('RouteTables', [])
        dependencies['route_tables'] = [
            rt['RouteTableId'] for rt in route_tables 
            if not rt.get('Associations', [{}])[0].get('Main', False)
        ]
        
        # Check network interfaces
        # Note: This may require EC2 client
        # dependencies['network_interfaces'] = [...]
        
        # Check VPC peering connections
        peerings = client.vpc.describe_vpc_peering_connections(
            filters=[
                {'name': 'requester-vpc-info.vpc-id', 'values': [vpc_id]},
                {'name': 'accepter-vpc-info.vpc-id', 'values': [vpc_id]}
            ]
        ).get('VpcPeeringConnections', [])
        dependencies['vpc_peering_connections'] = [
            p['VpcPeeringConnectionId'] for p in peerings
        ]
        
    except Exception as e:
        print(f"Warning: Could not check all dependencies: {e}")
    
    return dependencies
```

## Subnet Operations

### Create Subnet
```python
def create_subnet(client, vpc_id, cidr_block, availability_zone, subnet_name=None):
    """
    Create a subnet within a VPC.
    
    Args:
        client: CtyunClient instance
        vpc_id: Parent VPC ID
        cidr_block: Subnet CIDR (must be within VPC CIDR)
        availability_zone: AZ (e.g., 'cn-gz-a')
        subnet_name: Optional subnet name
    
    Returns:
        dict: Subnet creation response
    """
    # Validate CIDR is within VPC CIDR
    vpc = client.vpc.describe_vpcs(vpc_ids=[vpc_id])['Vpcs'][0]
    vpc_cidr = vpc['CidrBlock']
    
    if not is_subnet_within_vpc(cidr_block, vpc_cidr):
        raise ValueError(f"Subnet CIDR {cidr_block} not within VPC CIDR {vpc_cidr}")
    
    try:
        params = {
            'vpc_id': vpc_id,
            'cidr_block': cidr_block,
            'availability_zone': availability_zone
        }
        if subnet_name:
            params['name'] = subnet_name
            
        response = client.vpc.create_subnet(**params)
        subnet_id = response['Subnet']['SubnetId']
        print(f"Created subnet: {subnet_id}")
        
        # Wait for subnet to become available
        import time
        for i in range(30):
            subnet = client.vpc.describe_subnets(subnet_ids=[subnet_id])['Subnets'][0]
            if subnet['State'] == 'available':
                print(f"Subnet {subnet_id} is available")
                break
            print(f"Waiting for subnet to become available... ({i * 5}s)")
            time.sleep(5)
        
        return response
        
    except Exception as e:
        print(f"Failed to create subnet: {e}")
        raise

def is_subnet_within_vpc(subnet_cidr, vpc_cidr):
    """Check if subnet CIDR is within VPC CIDR range."""
    # Simplified check - in production use ipaddress module
    subnet_prefix = int(subnet_cidr.split('/')[1])
    vpc_prefix = int(vpc_cidr.split('/')[1])
    return subnet_prefix >= vpc_prefix  # More specific prefix means within
```

### List Subnets
```python
def list_subnets(client, vpc_id=None, subnet_ids=None, filters=None):
    """
    List subnets, optionally filtered by VPC.
    
    Args:
        client: CtyunClient instance
        vpc_id: Optional VPC ID to filter subnets
        subnet_ids: Optional list of subnet IDs
        filters: Additional filters
    
    Returns:
        list: Subnet objects
    """
    try:
        params = {}
        if subnet_ids:
            params['subnet_ids'] = subnet_ids
        
        filter_list = []
        if vpc_id:
            filter_list.append({'name': 'vpc-id', 'values': [vpc_id]})
        if filters:
            filter_list.extend(filters)
        if filter_list:
            params['filters'] = filter_list
            
        response = client.vpc.describe_subnets(**params)
        subnets = response.get('Subnets', [])
        
        print(f"Found {len(subnets)} subnet(s)")
        for subnet in subnets:
            print(f"  - {subnet['SubnetId']}: {subnet.get('Name', 'Unnamed')} "
                  f"({subnet['CidrBlock']}) in {subnet['AvailabilityZone']} - {subnet['State']}")
        
        return subnets
        
    except Exception as e:
        print(f"Failed to list subnets: {e}")
        raise
```

## Route Table Operations

### Create Route Table
```python
def create_route_table(client, vpc_id, name=None):
    """
    Create a custom route table.
    
    Args:
        client: CtyunClient instance
        vpc_id: VPC ID
        name: Optional route table name
    
    Returns:
        dict: Route table creation response
    """
    try:
        params = {'vpc_id': vpc_id}
        if name:
            params['name'] = name
            
        response = client.vpc.create_route_table(**params)
        route_table_id = response['RouteTable']['RouteTableId']
        print(f"Created route table: {route_table_id}")
        return response
        
    except Exception as e:
        print(f"Failed to create route table: {e}")
        raise
```

### Add Route
```python
def add_route(client, route_table_id, destination_cidr, target):
    """
    Add a route to a route table.
    
    Args:
        client: CtyunClient instance
        route_table_id: Route table ID
        destination_cidr: Destination CIDR (e.g., '0.0.0.0/0')
        target: Target ID (igw-*, nat-*, pcx-*, eni-*, etc.)
    
    Returns:
        dict: Route creation response
    """
    try:
        # Validate destination CIDR
        if destination_cidr == '0.0.0.0/0':
            print("WARNING: Adding default route (0.0.0.0/0)")
            
        response = client.vpc.create_route(
            route_table_id=route_table_id,
            destination_cidr_block=destination_cidr,
            gateway_id=target  # Could be gateway_id, instance_id, etc.
        )
        
        print(f"Added route {destination_cidr} -> {target} to {route_table_id}")
        return response
        
    except Exception as e:
        print(f"Failed to add route: {e}")
        raise
```

### Associate Route Table with Subnet
```python
def associate_route_table(client, route_table_id, subnet_id):
    """
    Associate a route table with a subnet.
    
    Args:
        client: CtyunClient instance
        route_table_id: Route table ID
        subnet_id: Subnet ID
    
    Returns:
        dict: Association response
    """
    try:
        response = client.vpc.associate_route_table(
            route_table_id=route_table_id,
            subnet_id=subnet_id
        )
        
        association_id = response['AssociationId']
        print(f"Associated route table {route_table_id} with subnet {subnet_id}")
        return response
        
    except Exception as e:
        print(f"Failed to associate route table: {e}")
        raise
```

## VPC Peering Operations

### Create VPC Peering Connection
```python
def create_vpc_peering(client, requester_vpc_id, accepter_vpc_id, peer_region=None):
    """
    Create a VPC peering connection.
    
    Args:
        client: CtyunClient instance
        requester_vpc_id: Requester VPC ID
        accepter_vpc_id: Accepter VPC ID
        peer_region: Region of accepter VPC (if cross-region)
    
    Returns:
        dict: Peering connection response
    """
    try:
        params = {
            'requester_vpc_id': requester_vpc_id,
            'accepter_vpc_id': accepter_vpc_id
        }
        if peer_region:
            params['peer_region'] = peer_region
            
        response = client.vpc.create_vpc_peering_connection(**params)
        peering_id = response['VpcPeeringConnection']['VpcPeeringConnectionId']
        print(f"Created VPC peering connection: {peering_id}")
        
        # If cross-account or manual acceptance required
        status = response['VpcPeeringConnection']['Status']['Code']
        if status == 'pending-acceptance':
            print(f"Peering {peering_id} requires acceptance by accepter VPC owner")
        
        return response
        
    except Exception as e:
        print(f"Failed to create VPC peering: {e}")
        raise
```

### Accept VPC Peering Connection
```python
def accept_vpc_peering(client, vpc_peering_connection_id):
    """
    Accept a VPC peering connection request.
    
    Args:
        client: CtyunClient instance
        vpc_peering_connection_id: Peering connection ID
    
    Returns:
        dict: Acceptance response
    """
    try:
        response = client.vpc.accept_vpc_peering_connection(
            vpc_peering_connection_id=vpc_peering_connection_id
        )
        
        print(f"Accepted VPC peering connection: {vpc_peering_connection_id}")
        return response
        
    except Exception as e:
        print(f"Failed to accept VPC peering: {e}")
        raise
```

## Error Handling Patterns

### SDK Error Handling
```python
def handle_sdk_error(operation, exception):
    """
    Handle SDK errors with appropriate messaging.
    
    Args:
        operation: Operation name (e.g., 'create_vpc')
        exception: Caught exception
    
    Returns:
        str: User-friendly error message
    """
    error_msg = str(exception).lower()
    
    if 'invalidparameter' in error_msg:
        return f"Invalid parameter for {operation}. Check your inputs."
    elif 'vpc limitexceeded' in error_msg:
        return f"VPC quota exceeded. Delete unused VPCs or request limit increase."
    elif 'cidrconflict' in error_msg or 'overlap' in error_msg:
        return f"CIDR conflict. Choose a non-overlapping IP range."
    elif 'dependencyviolation' in error_msg:
        return f"Cannot {operation} due to active dependencies. Remove dependencies first."
    elif 'notfound' in error_msg or '404' in error_msg:
        return f"Resource not found. Check the resource ID."
    elif 'accessdenied' in error_msg or 'unauthorized' in error_msg:
        return f"Access denied. Check IAM permissions for {operation}."
    elif 'requesttimeout' in error_msg or 'timeout' in error_msg:
        return f"Request timeout. Try again or increase timeout."
    elif 'internalservererror' in error_msg or '500' in error_msg:
        return f"Internal server error. Retry with exponential backoff."
    else:
        return f"Error during {operation}: {exception}"
```

### Retry Logic with Exponential Backoff
```python
import time
import random

def execute_with_retry(operation_func, max_retries=3, base_delay=1):
    """
    Execute operation with exponential backoff retry.
    
    Args:
        operation_func: Function to execute
        max_retries: Maximum retry attempts
        base_delay: Base delay in seconds
    
    Returns:
        Result of operation_func or raises exception
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                print(f"Retry attempt {attempt}/{max_retries} after {delay:.1f}s delay")
                time.sleep(delay)
            
            return operation_func()
            
        except Exception as e:
            last_exception = e
            error_msg = str(e).lower()
            
            # Determine if error is retryable
            if any(retryable in error_msg for retryable in [
                'requesttimeout', 
                'throttling', 
                'internalservererror',
                'temporary',
                'busy',
                '500',
                '503',
                '504'
            ]):
                if attempt < max_retries:
                    print(f"Retryable error: {e}")
                    continue
                else:
                    print(f"Max retries ({max_retries}) exceeded")
                    raise
            else:
                # Non-retryable error
                raise
    
    # Should not reach here
    raise last_exception

# Usage example
def create_vpc_with_retry(client, vpc_name, cidr_block):
    def _create():
        return client.vpc.create_vpc(name=vpc_name, cidr_block=cidr_block)
    
    return execute_with_retry(_create, max_retries=3, base_delay=2)
```