# VPC Troubleshooting Guide

## Overview
This guide covers common issues, error messages, and solutions for CTyun VPC operations.

## Common Error Patterns

### VPC Creation Errors

| Error | Cause | Solution |
|---|---|---|
| **InvalidParameter.CidrBlock** | Invalid CIDR format or range | Use RFC 1918 private ranges: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 |
| **VpcLimitExceeded** | Exceeded VPC quota per region | 1. Delete unused VPCs<br>2. Request quota increase via support ticket<br>3. Use existing VPCs where possible |
| **CidrConflict** | CIDR overlaps with existing VPC | Choose non-overlapping CIDR block |
| **InvalidParameter.Name** | Invalid VPC name | Names must be 1-128 characters, alphanumeric, hyphens, underscores |
| **AccessDenied** | Insufficient IAM permissions | Add `vpc:CreateVpc` permission to IAM policy |

### Subnet Creation Errors

| Error | Cause | Solution |
|---|---|---|
| **InvalidParameter.CidrBlock** | Subnet CIDR not within VPC CIDR | Ensure subnet CIDR is subset of VPC CIDR (e.g., VPC: 10.0.0.0/16, Subnet: 10.0.1.0/24) |
| **CidrConflict** | Subnet CIDR overlaps with existing subnet | Choose non-overlapping CIDR within VPC |
| **InvalidSubnet.Range** | Subnet size invalid | Subnet must be /16 to /28 inclusive |
| **SubnetLimitExceeded** | Exceeded subnet quota per VPC | 1. Delete unused subnets<br>2. Request quota increase<br>3. Use larger subnets to reduce count |
| **InvalidParameter.AvailabilityZone** | Invalid or unavailable AZ | Use valid AZ for region (e.g., cn-gz-a, cn-gz-b) |

### VPC Deletion Errors

| Error | Cause | Solution |
|---|---|---|
| **DependencyViolation** | Active resources in VPC | Remove all: subnets, route tables, network interfaces, peering connections |
| **InvalidVpcID.NotFound** | VPC not found or already deleted | Verify VPC ID exists and is in correct region |
| **OperationNotPermitted** | Default VPC cannot be deleted | Default VPC is protected; create new VPC instead |
| **VpcInUse** | VPC has active instances or resources | Terminate all instances, delete all resources first |

### Route Table Errors

| Error | Cause | Solution |
|---|---|---|
| **InvalidRoute.NotFound** | Route target not found | Verify gateway, instance, or peering connection exists |
| **RouteAlreadyExists** | Duplicate route | Each route table can have only one route per destination CIDR |
| **InvalidParameter.DestinationCidrBlock** | Invalid destination CIDR | Use valid CIDR notation (e.g., 10.0.0.0/16, 0.0.0.0/0) |
| **RouteLimitExceeded** | Exceeded routes per route table | 1. Consolidate routes<br>2. Use multiple route tables<br>3. Request quota increase |

### VPC Peering Errors

| Error | Cause | Solution |
|---|---|---|
| **InvalidVpcPeeringConnectionID.NotFound** | Peering connection not found | Verify peering ID exists and is in correct region |
| **PeeringCidrConflict** | Overlapping CIDR blocks between VPCs | VPCs must have non-overlapping CIDR ranges to peer |
| **InvalidState** | Peering connection in invalid state | Check status: pending-acceptance, active, rejected, failed |
| **OperationNotPermitted** | Cross-account peering not accepted | Accepter must accept peering request |

## Connectivity Issues

### Instance Cannot Reach Internet

| Symptom | Check | Solution |
|---|---|---|
| **No internet from public subnet** | 1. Internet Gateway attached to VPC?<br>2. Route table has 0.0.0.0/0 -> igw-*?<br>3. Subnet associated with correct route table? | 1. Create and attach Internet Gateway<br>2. Add default route to Internet Gateway<br>3. Associate subnet with route table |
| **No internet from private subnet** | 1. NAT Gateway exists?<br>2. Route table has 0.0.0.0/0 -> nat-*?<br>3. NAT Gateway in public subnet? | 1. Create NAT Gateway in public subnet<br>2. Add default route to NAT Gateway<br>3. Ensure NAT Gateway has Elastic IP |
| **Intermittent connectivity** | 1. Network ACL blocking traffic?<br>2. Security group rules correct?<br>3. Instance network configuration? | 1. Check network ACL inbound/outbound rules<br>2. Verify security group allows traffic<br>3. Check instance OS network config |

### Cross-VPC Connectivity Issues

| Symptom | Check | Solution |
|---|---|---|
| **Cannot reach peered VPC** | 1. Peering connection active?<br>2. Route tables updated?<br>3. Network ACLs allow traffic? | 1. Accept peering request if pending<br>2. Add routes in both VPCs pointing to peering connection<br>3. Update network ACLs to allow cross-VPC traffic |
| **One-way connectivity only** | 1. Routes configured both ways?<br>2. Network ACLs symmetric?<br>3. Security groups allow return traffic? | 1. Add routes in both VPCs<br>2. Ensure network ACLs allow bidirectional traffic<br>3. Security groups must allow return traffic |
| **DNS resolution failing** | 1. Enable DNS hostnames?<br>2. Enable DNS support?<br>3. Cross-VPC DNS resolution enabled? | 1. Enable DNS hostnames in VPC<br>2. Enable DNS support in VPC<br>3. For private hosted zones, ensure proper configuration |

### Subnet Connectivity Issues

| Symptom | Check | Solution |
|---|---|---|
| **Instances in same subnet cannot communicate** | 1. Network ACL blocking intra-subnet?<br>2. Security group rules?<br>3. Instance firewall? | 1. Network ACL must allow intra-subnet traffic (rule 100)<br>2. Security groups must allow traffic<br>3. Check instance OS firewall |
| **Instances in different subnets cannot communicate** | 1. Route table routes?<br>2. Network ACLs allow cross-subnet?<br>3. Subnets in same VPC? | 1. Route table should have local route for VPC CIDR<br>2. Network ACLs must allow cross-subnet traffic<br>3. Subnets must be in same VPC |
| **Cannot ping instances** | 1. ICMP allowed in security group?<br>2. ICMP allowed in network ACL?<br>3. Instance responding to ICMP? | 1. Security group must allow ICMP (type 8)<br>2. Network ACL must allow ICMP<br>3. Instance OS must respond to ping |

## Performance Issues

### High Latency Between AZs

| Issue | Investigation | Solution |
|---|---|---|
| **Cross-AZ latency >5ms** | 1. Normal for cross-AZ traffic<br>2. Check for packet loss<br>3. Monitor VPC Flow Logs | 1. Design for cross-AZ latency tolerance<br>2. Use same AZ for latency-sensitive components<br>3. Consider placement groups |
| **Packet loss between subnets** | 1. Network ACL dropping packets?<br>2. MTU mismatch?<br>3. Bandwidth saturation? | 1. Check network ACL rules and counters<br>2. Ensure consistent MTU (usually 1500)<br>3. Monitor network bandwidth usage |
| **Intermittent timeouts** | 1. DNS resolution delays?<br>2. Connection tracking limits?<br>3. Instance resource constraints? | 1. Check DNS resolution times<br>2. Monitor connection tracking table<br>3. Check instance CPU/memory/network |

### Bandwidth Limitations

| Limitation | Default | Notes |
|---|---|---|
| **VPC bandwidth** | 5 Gbps per flow | Can burst to 10 Gbps |
| **Cross-AZ bandwidth** | Lower than intra-AZ | Traffic between AZs uses inter-AZ network |
| **Internet Gateway bandwidth** | 5 Gbps | Scales with multiple Internet Gateways |
| **VPC Peering bandwidth** | 5 Gbps | Depends on instance types and peering path |

## Security and Access Issues

### IAM Permission Issues

| Error | Required Permission | Notes |
|---|---|---|
| **AccessDenied: vpc:CreateVpc** | `vpc:CreateVpc` | Also need `vpc:DescribeVpcs` to verify |
| **AccessDenied: vpc:DeleteVpc** | `vpc:DeleteVpc` | May need `vpc:Describe*` to check dependencies |
| **AccessDenied: vpc:CreateSubnet** | `vpc:CreateSubnet` | Also need `vpc:DescribeSubnets` |
| **AccessDenied: vpc:CreateRoute** | `vpc:CreateRoute` | May need `ec2:Describe*` for target validation |
| **AccessDenied: vpc:CreateVpcPeeringConnection** | `vpc:CreateVpcPeeringConnection` | Accepter needs `vpc:AcceptVpcPeeringConnection` |

### Network ACL Configuration Issues

| Symptom | Common Mistake | Fix |
|---|---|---|
| **All traffic blocked** | No allow rules | Add rule 100: ALLOW ALL for testing |
| **HTTP/HTTPS not working** | Missing port 80/443 | Add rules for ports 80 (HTTP) and 443 (HTTPS) |
| **DNS not working** | Missing port 53 | Add rules for UDP/TCP port 53 |
| **Ephemeral port issues** | Missing outbound rules for ephemeral ports | Allow outbound traffic to ports 1024-65535 |
| **Rule evaluation order** | Deny rule before allow rule | Rules evaluated in ascending order; place allows before denies |

### Security Group vs Network ACL Conflicts

| Conflict | Resolution |
|---|---|
| **Security Group allows but Network ACL denies** | Network ACL takes precedence; update Network ACL |
| **Network ACL allows but Security Group denies** | Security Group takes precedence; update Security Group |
| **Both allow but still blocked** | Check instance OS firewall, route tables, and VPC Flow Logs |
| **Stateful vs Stateless confusion** | Security Groups are stateful (return traffic auto-allowed); Network ACLs are stateless (need explicit return rules) |

## Diagnostic Commands and Tools

### SDK Diagnostic Functions

```python
def diagnose_vpc_connectivity(client, vpc_id, source_subnet, dest_ip):
    """
    Diagnose connectivity between subnet and destination IP.
    
    Args:
        client: CtyunClient instance
        vpc_id: VPC ID
        source_subnet: Source subnet ID
        dest_ip: Destination IP address
    
    Returns:
        dict: Diagnostic results
    """
    results = {
        'vpc_exists': False,
        'subnet_exists': False,
        'route_table': None,
        'routes': [],
        'network_acls': [],
        'security_groups': []
    }
    
    try:
        # Check VPC exists
        vpcs = client.vpc.describe_vpcs(vpc_ids=[vpc_id])['Vpcs']
        results['vpc_exists'] = len(vpcs) > 0
        
        # Check subnet exists
        subnets = client.vpc.describe_subnets(subnet_ids=[source_subnet])['Subnets']
        results['subnet_exists'] = len(subnets) > 0
        
        if subnets:
            subnet = subnets[0]
            # Get route table
            route_tables = client.vpc.describe_route_tables(
                filters=[{'name': 'association.subnet-id', 'values': [source_subnet]}]
            )['RouteTables']
            
            if route_tables:
                route_table = route_tables[0]
                results['route_table'] = route_table['RouteTableId']
                results['routes'] = route_table.get('Routes', [])
            
            # Get network ACL
            network_acls = client.vpc.describe_network_acls(
                filters=[{'name': 'association.subnet-id', 'values': [source_subnet]}]
            )['NetworkAcls']
            
            if network_acls:
                results['network_acls'] = network_acls[0].get('Entries', [])
        
        return results
        
    except Exception as e:
        print(f"Diagnostic failed: {e}")
        return results
```

### VPC Flow Log Analysis

```python
def analyze_flow_logs(log_group, vpc_id, time_range='1h'):
    """
    Analyze VPC Flow Logs for connectivity issues.
    
    Args:
        log_group: CloudWatch Log Group name
        vpc_id: VPC ID to filter logs
        time_range: Time range to query (e.g., '1h', '24h')
    
    Returns:
        dict: Analysis results
    """
    # This is a conceptual example - actual implementation depends on
    # CloudWatch Logs Insights query syntax
    
    query = f"""
    fields @timestamp, srcAddr, dstAddr, srcPort, dstPort, protocol, action, logStatus
    | filter vpcId = '{vpc_id}'
    | filter action = 'REJECT'
    | stats count() by srcAddr, dstAddr, dstPort, protocol
    | sort @timestamp desc
    | limit 100
    """
    
    print(f"Querying VPC Flow Logs for VPC {vpc_id}")
    print(f"Query: {query}")
    
    # In practice, use boto3 to query CloudWatch Logs Insights
    # import boto3
    # client = boto3.client('logs')
    # response = client.start_query(...)
    
    return {
        'query': query,
        'suggested_filters': [
            f"vpcId = '{vpc_id}'",
            "action = 'REJECT'",
            "logStatus != 'OK'"
        ]
    }
```

## Recovery Procedures

### Accidentally Deleted VPC

| Scenario | Recovery Options | Notes |
|---|---|---|
| **VPC deleted with resources** | 1. Restore from backup if available<br>2. Recreate VPC with same CIDR<br>3. Recreate resources manually | VPC deletion is irreversible; no recycle bin |
| **Default VPC deleted** | 1. Create new VPC as replacement<br>2. Update configurations to use new VPC<br>3. Some services may require default VPC | Default VPC can be recreated via support request |
| **Critical subnet deleted** | 1. Create new subnet with same/similar CIDR<br>2. Update route table associations<br>3. Migrate resources to new subnet | Subnet deletion is irreversible |

### CIDR Conflict Resolution

| Conflict Type | Resolution Steps |
|---|---|
| **VPC CIDR overlaps with corporate network** | 1. Choose new non-overlapping CIDR<br>2. Create new VPC with new CIDR<br>3. Migrate resources to new VPC<br>4. Update DNS and configurations |
| **Subnet CIDR overlaps within VPC** | 1. Identify overlapping subnets<br>2. Delete or resize one subnet<br>3. Ensure no active resources in subnet before deletion |
| **VPC Peering CIDR overlap** | 1. VPCs cannot peer if CIDRs overlap<br>2. Consider VPN instead of peering<br>3. Or redesign network with non-overlapping CIDRs |

### Route Table Corruption

| Symptom | Recovery Steps |
|---|---|
| **Missing default route** | 1. Identify correct Internet Gateway/NAT Gateway<br>2. Add route 0.0.0.0/0 -> gateway-id<br>3. Verify connectivity |
| **Circular routing** | 1. Analyze route tables for loops<br>2. Remove or fix circular routes<br>3. Test connectivity after fix |
| **Route table disassociated** | 1. Reassociate route table with subnet<br>2. Verify subnet uses correct route table<br>3. Test connectivity |

## Prevention Best Practices

### Before Making Changes

1. **Take snapshots/backups** of critical configurations
2. **Document current state** - VPC IDs, subnet IDs, route tables, network ACLs
3. **Test in non-production** environment first
4. **Use change windows** for production changes
5. **Have rollback plan** documented

### Monitoring and Alerting

1. **Enable VPC Flow Logs** for all critical VPCs
2. **Monitor VPC metrics** - packet counts, bytes, error rates
3. **Set up alerts** for:
   - VPC deletion attempts
   - Route table changes
   - Network ACL changes
   - High error/reject rates in flow logs
4. **Regular audit** of VPC configurations and security rules

### Security Hardening

1. **Least privilege** IAM policies for VPC operations
2. **Network segmentation** - separate tiers into different subnets
3. **Defense in depth** - combine Security Groups and Network ACLs
4. **Regular review** of network ACL and security group rules
5. **Enable DNS query logging** for troubleshooting

## Support Resources

- **CTyun VPC Documentation**: https://www.ctyun.cn/document/10026791
- **VPC API Reference**: https://www.ctyun.cn/document/10026791/10027466
- **Network Troubleshooting Guide**: https://www.ctyun.cn/document/10026791/10027470
- **Support Tickets**: For quota increases, default VPC recovery, critical issues

## Version History

| Version | Date | Change |
|---|---|---|
| v1 | 2026-06-05 | Initial VPC troubleshooting guide |