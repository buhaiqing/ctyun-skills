# VPC Monitoring Guide

## Overview
Comprehensive monitoring strategy for CTyun VPC resources, including metrics, alarms, dashboards, and troubleshooting.

## Key VPC Metrics

### Network Performance Metrics

| Metric | Description | Normal Range | Critical Threshold |
|---|---|---|---|
| **NetworkInBytes** | Bytes received by instances | Varies by instance type | Sudden drop to 0 (connectivity loss) |
| **NetworkOutBytes** | Bytes sent by instances | Varies by instance type | Sudden drop to 0 (connectivity loss) |
| **NetworkPacketsIn** | Packets received | Varies by traffic | >10% packet loss |
| **NetworkPacketsOut** | Packets sent | Varies by traffic | >10% packet loss |
| **NetworkInErrors** | Receive errors | 0 | >0 sustained |
| **NetworkOutErrors** | Transmit errors | 0 | >0 sustained |
| **NetworkInDropped** | Dropped inbound packets | 0 | >0 sustained |
| **NetworkOutDropped** | Dropped outbound packets | 0 | >0 sustained |

### VPC-Specific Metrics

| Metric | Description | Source | Alert Threshold |
|---|---|---|---|
| **VPCPeeringConnectionStatus** | Peering connection health | VPC API | Status != 'active' for >5min |
| **VPCBandwidthUtilization** | Bandwidth usage percentage | Flow Logs | >80% for 15min |
| **VPCPacketLossRate** | Packet loss percentage | Flow Logs | >5% for 5min |
| **VPCConnections** | Active connections count | Flow Logs | Sudden drop >50% |
| **VPCRejectedConnections** | Rejected connection attempts | Flow Logs | >100/min sustained |
| **VPCFlowLogDelivery** | Flow log delivery status | CloudWatch Logs | Delivery failure >10min |

### Subnet Metrics

| Metric | Description | Alert Condition |
|---|---|---|
| **SubnetAvailableIPs** | Available IP addresses in subnet | <10% of total IPs |
| **SubnetIPUtilization** | IP address utilization percentage | >90% for 1 hour |
| **SubnetInstanceCount** | Instances in subnet | Sudden drop to 0 (all instances failed) |
| **SubnetNetworkThroughput** | Throughput per subnet | >80% of limit for 15min |

## CloudWatch Alarms Configuration

### Critical Alarms (P0)

```python
# VPC Deletion Attempt Alarm
vpc_deletion_alarm = {
    'AlarmName': 'VPC-Deletion-Attempt',
    'MetricName': 'VpcEventCount',
    'Namespace': 'CTyun/VPC',
    'Statistic': 'Sum',
    'Period': 300,  # 5 minutes
    'EvaluationPeriods': 1,
    'Threshold': 0,
    'ComparisonOperator': 'GreaterThanThreshold',
    'AlarmActions': ['arn:aws:sns:region:account:critical-alerts'],
    'Dimensions': [
        {'Name': 'EventName', 'Value': 'DeleteVpc'},
        {'Name': 'VpcId', 'Value': 'vpc-12345678'}
    ]
}

# VPC Peering Connection Failure
peering_failure_alarm = {
    'AlarmName': 'VPC-Peering-Failure',
    'MetricName': 'VPCPeeringConnectionStatus',
    'Namespace': 'CTyun/VPC',
    'Statistic': 'Minimum',
    'Period': 300,
    'EvaluationPeriods': 2,  # 10 minutes
    'Threshold': 1,  # 1 = active, 0 = not active
    'ComparisonOperator': 'LessThanThreshold',
    'AlarmActions': ['arn:aws:sns:region:account:critical-alerts'],
    'Dimensions': [
        {'Name': 'VpcPeeringConnectionId', 'Value': 'pcx-12345678'}
    ]
}
```

### Warning Alarms (P1)

```python
# High Bandwidth Utilization
bandwidth_alarm = {
    'AlarmName': 'VPC-High-Bandwidth',
    'MetricName': 'VPCBandwidthUtilization',
    'Namespace': 'CTyun/VPC',
    'Statistic': 'Average',
    'Period': 300,
    'EvaluationPeriods': 3,  # 15 minutes
    'Threshold': 80.0,  # 80% utilization
    'ComparisonOperator': 'GreaterThanThreshold',
    'AlarmActions': ['arn:aws:sns:region:account:warning-alerts'],
    'OKActions': ['arn:aws:sns:region:account:warning-alerts'],
    'Dimensions': [
        {'Name': 'VpcId', 'Value': 'vpc-12345678'}
    ]
}

# Subnet IP Exhaustion
subnet_ip_alarm = {
    'AlarmName': 'Subnet-IP-Exhaustion',
    'MetricName': 'SubnetAvailableIPs',
    'Namespace': 'CTyun/VPC',
    'Statistic': 'Minimum',
    'Period': 3600,  # 1 hour
    'EvaluationPeriods': 1,
    'Threshold': 10,  # Less than 10 IPs available
    'ComparisonOperator': 'LessThanThreshold',
    'AlarmActions': ['arn:aws:sns:region:account:warning-alerts'],
    'Dimensions': [
        {'Name': 'SubnetId', 'Value': 'subnet-12345678'}
    ]
}
```

### Informational Alarms (P2)

```python
# Network Error Rate Increase
network_error_alarm = {
    'AlarmName': 'Network-Error-Increase',
    'MetricName': 'NetworkInErrors',
    'Namespace': 'CTyun/EC2',
    'Statistic': 'Sum',
    'Period': 300,
    'EvaluationPeriods': 2,
    'Threshold': 100,  # More than 100 errors in 10min
    'ComparisonOperator': 'GreaterThanThreshold',
    'AlarmActions': ['arn:aws:sns:region:account:info-alerts'],
    'Dimensions': [
        {'Name': 'VpcId', 'Value': 'vpc-12345678'}
    ]
}

# Flow Log Delivery Failure
flowlog_alarm = {
    'AlarmName': 'FlowLog-Delivery-Failure',
    'MetricName': 'VPCFlowLogDelivery',
    'Namespace': 'CTyun/VPC',
    'Statistic': 'Minimum',
    'Period': 600,  # 10 minutes
    'EvaluationPeriods': 1,
    'Threshold': 1,  # 1 = delivering, 0 = failed
    'ComparisonOperator': 'LessThanThreshold',
    'AlarmActions': ['arn:aws:sns:region:account:info-alerts'],
    'Dimensions': [
        {'Name': 'VpcId', 'Value': 'vpc-12345678'},
        {'Name': 'LogGroup', 'Value': 'VPCFlowLogs'}
    ]
}
```

## VPC Flow Logs Analysis

### Enabling Flow Logs

```python
def enable_vpc_flow_logs(client, vpc_id, log_group_name, traffic_type='ALL'):
    """
    Enable VPC Flow Logs for a VPC.
    
    Args:
        client: CtyunClient instance
        vpc_id: VPC ID
        log_group_name: CloudWatch Log Group name
        traffic_type: 'ALL', 'ACCEPT', or 'REJECT'
    
    Returns:
        str: Flow Log ID
    """
    try:
        response = client.vpc.create_flow_logs(
            resource_ids=[vpc_id],
            resource_type='VPC',
            traffic_type=traffic_type,
            log_group_name=log_group_name,
            deliver_logs_permission_arn='arn:aws:iam::account:role/FlowLogRole',
            # Optional: log_destination_type='cloud-watch-logs',
            # Optional: max_aggregation_interval=600
        )
        
        flow_log_id = response['FlowLogIds'][0]
        print(f"Enabled Flow Logs for VPC {vpc_id}: {flow_log_id}")
        return flow_log_id
        
    except Exception as e:
        print(f"Failed to enable Flow Logs: {e}")
        raise
```

### Flow Log Query Examples

#### Top Talkers Analysis
```sql
-- Find top source-destination pairs
fields @timestamp, srcAddr, dstAddr, bytes
| stats sum(bytes) as totalBytes by srcAddr, dstAddr
| sort totalBytes desc
| limit 20
```

#### Security Threat Detection
```sql
-- Detect port scanning
fields @timestamp, srcAddr, dstAddr, dstPort, action
| filter action = 'REJECT'
| stats count() as rejectCount by srcAddr, dstAddr, dstPort
| filter rejectCount > 100
| sort rejectCount desc
```

#### Performance Issues
```sql
-- Find high packet loss
fields @timestamp, srcAddr, dstAddr, packets, lostPackets
| filter lostPackets > 0
| stats sum(lostPackets) as totalLost, sum(packets) as totalPackets 
    by srcAddr, dstAddr
| display totalLost, totalPackets, (totalLost*100.0/totalPackets) as lossPercent
| filter lossPercent > 5.0
```

## Dashboard Configuration

### VPC Health Dashboard

**Key Widgets:**
1. **VPC Status Summary**
   - Total VPCs
   - VPCs with active issues
   - Recent changes (last 24h)

2. **Network Performance**
   - Bandwidth utilization (in/out)
   - Packet loss rate
   - Error rates

3. **Subnet Utilization**
   - IP address utilization per subnet
   - Instance count per subnet
   - Available IP forecast

4. **Security Monitoring**
   - Rejected connection attempts
   - Unusual traffic patterns
   - Flow log delivery status

5. **Peering Connections**
   - Peering status (active/pending/failed)
   - Cross-VPC traffic volume
   - Peering latency

### Implementation Example

```python
def create_vpc_dashboard(client, vpc_id, dashboard_name):
    """
    Create a CloudWatch Dashboard for VPC monitoring.
    
    Args:
        client: CloudWatch client
        vpc_id: VPC ID to monitor
        dashboard_name: Dashboard name
    
    Returns:
        dict: Dashboard creation response
    """
    dashboard_body = {
        'widgets': [
            {
                'type': 'metric',
                'x': 0, 'y': 0, 'width': 12, 'height': 6,
                'properties': {
                    'metrics': [
                        ['CTyun/VPC', 'NetworkInBytes', 'VpcId', vpc_id],
                        ['.', 'NetworkOutBytes', '.', '.']
                    ],
                    'period': 300,
                    'stat': 'Average',
                    'region': 'cn-gz',
                    'title': f'VPC {vpc_id} - Network Throughput',
                    'view': 'timeSeries',
                    'stacked': False
                }
            },
            {
                'type': 'metric',
                'x': 12, 'y': 0, 'width': 12, 'height': 6,
                'properties': {
                    'metrics': [
                        ['CTyun/VPC', 'NetworkInErrors', 'VpcId', vpc_id],
                        ['.', 'NetworkOutErrors', '.', '.']
                    ],
                    'period': 300,
                    'stat': 'Sum',
                    'region': 'cn-gz',
                    'title': f'VPC {vpc_id} - Network Errors',
                    'view': 'timeSeries',
                    'stacked': False
                }
            },
            {
                'type': 'text',
                'x': 0, 'y': 6, 'width': 24, 'height': 3,
                'properties': {
                    'markdown': f'# VPC {vpc_id} Monitoring\\n'
                               f'**Last Updated**: {datetime.now().isoformat()}\\n'
                               f'**Region**: cn-gz\\n'
                               f'**Monitoring Status**: Active'
                }
            }
        ]
    }
    
    try:
        response = client.put_dashboard(
            DashboardName=dashboard_name,
            DashboardBody=json.dumps(dashboard_body)
        )
        print(f"Created dashboard: {dashboard_name}")
        return response
        
    except Exception as e:
        print(f"Failed to create dashboard: {e}")
        raise
```

## Automated Response Actions

### Auto-Remediation Scripts

```python
def auto_remediate_subnet_full(client, subnet_id):
    """
    Automatically remediate subnet IP exhaustion.
    
    Args:
        client: CtyunClient instance
        subnet_id: Subnet ID that's full
    
    Returns:
        bool: True if remediation successful
    """
    try:
        # Get subnet details
        subnet = client.vpc.describe_subnets(subnet_ids=[subnet_id])['Subnets'][0]
        vpc_id = subnet['VpcId']
        az = subnet['AvailabilityZone']
        cidr = subnet['CidrBlock']
        
        # Calculate new CIDR (next available in VPC)
        # This is simplified - actual implementation needs CIDR calculation logic
        new_cidr = calculate_next_available_cidr(vpc_id, cidr)
        
        if not new_cidr:
            print(f"Cannot find available CIDR in VPC {vpc_id}")
            return False
        
        # Create new subnet
        new_subnet = client.vpc.create_subnet(
            vpc_id=vpc_id,
            cidr_block=new_cidr,
            availability_zone=az,
            name=f"{subnet.get('Name', 'subnet')}-expansion-{datetime.now().strftime('%Y%m%d')}"
        )
        
        new_subnet_id = new_subnet['Subnet']['SubnetId']
        
        # Copy route table association
        route_tables = client.vpc.describe_route_tables(
            filters=[{'name': 'association.subnet-id', 'values': [subnet_id]}]
        )['RouteTables']
        
        if route_tables:
            route_table_id = route_tables[0]['RouteTableId']
            client.vpc.associate_route_table(
                route_table_id=route_table_id,
                subnet_id=new_subnet_id
            )
        
        # Copy network ACL association
        network_acls = client.vpc.describe_network_acls(
            filters=[{'name': 'association.subnet-id', 'values': [subnet_id]}]
        )['NetworkAcls']
        
        if network_acls:
            network_acl_id = network_acls[0]['NetworkAclId']
            # Note: Network ACL association may need different API
        
        print(f"Created new subnet {new_subnet_id} ({new_cidr}) for expansion")
        return True
        
    except Exception as e:
        print(f"Auto-remediation failed: {e}")
        return False
```

### Incident Response Playbook

| Incident Type | Automated Response | Manual Steps Required |
|---|---|---|
| **VPC deletion attempt** | 1. Block API call if unauthorized<br>2. Alert security team<br>3. Freeze IAM user | 1. Investigate IAM user<br>2. Check CloudTrail logs<br>3. Restore from backup if needed |
| **VPC peering failure** | 1. Attempt automatic reconnection<br>2. Route traffic through VPN backup | 1. Diagnose peering issue<br>2. Coordinate with peer VPC owner<br>3. Update DNS if needed |
| **Subnet IP exhaustion** | 1. Create new subnet automatically<br>2. Update auto-scaling groups | 1. Verify new subnet connectivity<br>2. Migrate critical services<br>3. Clean up old subnet |
| **High packet loss** | 1. Route traffic to healthy AZ<br>2. Scale out instances | 1. Diagnose network issue<br>2. Contact CTyun support<br>3. Update architecture if chronic |

## Capacity Planning

### IP Address Forecasting

```python
def forecast_ip_usage(subnet_id, growth_rate=0.1, forecast_days=90):
    """
    Forecast IP address usage for a subnet.
    
    Args:
        subnet_id: Subnet ID
        growth_rate: Daily growth rate (decimal)
        forecast_days: Days to forecast
    
    Returns:
        dict: Forecast results
    """
    try:
        subnet = client.vpc.describe_subnets(subnet_ids=[subnet_id])['Subnets'][0]
        available_ips = subnet['AvailableIpAddressCount']
        total_ips = calculate_total_ips(subnet['CidrBlock'])
        used_ips = total_ips - available_ips
        
        forecast = {
            'current': {
                'used': used_ips,
                'available': available_ips,
                'utilization': (used_ips / total_ips) * 100
            },
            'forecast': []
        }
        
        current_used = used_ips
        for day in range(1, forecast_days + 1):
            current_used *= (1 + growth_rate)
            available = total_ips - current_used
            utilization = (current_used / total_ips) * 100
            
            forecast['forecast'].append({
                'day': day,
                'estimated_used': int(current_used),
                'estimated_available': int(available),
                'estimated_utilization': utilization,
                'status': 'OK' if available > (total_ips * 0.1) else 'WARNING' if available > 0 else 'CRITICAL'
            })
        
        return forecast
        
    except Exception as e:
        print(f"Forecast failed: {e}")
        return None

def calculate_total_ips(cidr_block):
    """Calculate total IPs in a CIDR block."""
    # Simplified calculation
    prefix = int(cidr_block.split('/')[1])
    return 2 ** (32 - prefix) - 5  # Subtract 5 reserved addresses
```

### Bandwidth Planning

| Instance Type | Baseline Bandwidth | Burst Bandwidth | Recommended Use |
|---|---|---|---|
| **Small (1-2 vCPU)** | 0.5-1 Gbps | Up to 5 Gbps | Development, testing |
| **Medium (4-8 vCPU)** | 1-2 Gbps | Up to 10 Gbps | Application servers |
| **Large (16+ vCPU)** | 5 Gbps | Up to 25 Gbps | Database, caching |
| **Network Optimized** | 10-25 Gbps | Up to 100 Gbps | Network appliances, load balancers |

### VPC Peering Bandwidth
| Peering Type | Baseline Bandwidth | Notes |
|---|---|---|
| **Intra-region** | 5 Gbps | Can burst to 10 Gbps |
| **Cross-region** | 1 Gbps | May have higher latency |
| **Cross-account** | Same as intra-region | Subject to both accounts' limits |

## Integration Monitoring

### With Cloud Monitor
```python
def setup_vpc_cloud_monitor_alarms(client, vpc_id):
    """
    Set up Cloud Monitor alarms for VPC.
    
    Args:
        client: CloudMonitor client
        vpc_id: VPC ID to monitor
    """
    alarms = [
        {
            'name': f'vpc-{vpc_id}-high-bandwidth',
            'metric': 'vpc.bandwidth.utilization',
            'threshold': 80.0,
            'period': 300,
            'evaluation_periods': 3,
            'statistic': 'Average',
            'comparison': 'GreaterThanThreshold',
            'dimensions': {'vpcId': vpc_id}
        },
        {
            'name': f'vpc-{vpc_id}-packet-loss',
            'metric': 'vpc.packet.loss.rate',
            'threshold': 5.0,
            'period': 300,
            'evaluation_periods': 2,
            'statistic': 'Average',
            'comparison': 'GreaterThanThreshold',
            'dimensions': {'vpcId': vpc_id}
        },
        {
            'name': f'vpc-{vpc_id}-peering-status',
            'metric': 'vpc.peering.connection.status',
            'threshold': 1,  # 1 = active
            'period': 300,
            'evaluation_periods': 2,
            'statistic': 'Minimum',
            'comparison': 'LessThanThreshold',
            'dimensions': {'vpcId': vpc_id}
        }
    ]
    
    for alarm_config in alarms:
        try:
            client.put_alarm(**alarm_config)
            print(f"Created alarm: {alarm_config['name']}")
        except Exception as e:
            print(f"Failed to create alarm {alarm_config['name']}: {e}")
```

### With Log Service
```python
def analyze_vpc_flow_logs_sls(log_store, vpc_id, start_time, end_time):
    """
    Analyze VPC Flow Logs using CTyun Log Service.
    
    Args:
        log_store: Log Service store name
        vpc_id: VPC ID to analyze
        start_time: Start time for query
        end_time: End time for query
    
    Returns:
        dict: Analysis results
    """
    query = f"""
    * | where vpcId = '{vpc_id}'
    | summarize 
        totalBytes = sum(bytes),
        totalPackets = sum(packets),
        rejectedCount = countif(action = 'REJECT'),
        acceptedCount = countif(action = 'ACCEPT')
    by srcAddr, dstAddr, srcPort, dstPort, protocol
    | sort by totalBytes desc
    | limit 100
    """
    
    # Execute query via Log Service API
    # This is conceptual - actual implementation uses CTyun Log Service SDK
    
    return {
        'query': query,
        'time_range': f'{start_time} to {end_time}',
        'vpc_id': vpc_id
    }
```

## Health Checks and Automation

### Daily Health Check Script
```python
def daily_vpc_health_check(client, vpc_ids):
    """
    Perform daily health check on VPCs.
    
    Args:
        client: CtyunClient instance
        vpc_ids: List of VPC IDs to check
    
    Returns:
        dict: Health check results
    """
    results = {}
    
    for vpc_id in vpc_ids:
        vpc_health = {
            'vpc_id': vpc_id,
            'status': 'HEALTHY',
            'issues': [],
            'metrics': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Check VPC existence and state
            vpc_info = client.vpc.describe_vpcs(vpc_ids=[vpc_id])['Vpcs'][0]
            if vpc_info['State'] != 'available':
                vpc_health['status'] = 'UNHEALTHY'
                vpc_health['issues'].append(f"VPC state is {vpc_info['State']}")
            
            # Check subnets
            subnets = client.vpc.describe_subnets(
                filters=[{'name': 'vpc-id', 'values': [vpc_id]}]
            )['Subnets']
            
            full_subnets = []
            for subnet in subnets:
                available_ips = subnet['AvailableIpAddressCount']
                total_ips = calculate_total_ips(subnet['CidrBlock'])
                utilization = ((total_ips - available_ips) / total_ips) * 100
                
                if utilization > 90:
                    full_subnets.append({
                        'subnet_id': subnet['SubnetId'],
                        'utilization': utilization
                    })
            
            if full_subnets:
                vpc_health['status'] = 'WARNING'
                vpc_health['issues'].append(f"{len(full_subnets)} subnets >90% full")
                vpc_health['metrics']['full_subnets'] = full_subnets
            
            # Check peering connections
            peerings = client.vpc.describe_vpc_peering_connections(
                filters=[
                    {'name': 'requester-vpc-info.vpc-id', 'values': [vpc_id]},
                    {'name': 'accepter-vpc-info.vpc-id', 'values': [vpc_id]}
                ]
            )['VpcPeeringConnections']
            
            failed_peerings = [
                p for p in peerings 
                if p['Status']['Code'] not in ['active', 'provisioning']
            ]
            
            if failed_peerings:
                vpc_health['status'] = 'UNHEALTHY'
                vpc_health['issues'].append(
                    f"{len(failed_peerings)} peering connections not active"
                )
            
            results[vpc_id] = vpc_health
            
        except Exception as e:
            results[vpc_id] = {
                'vpc_id': vpc_id,
                'status': 'ERROR',
                'issues': [f"Health check failed: {str(e)}"],
                'timestamp': datetime.now().isoformat()
            }
    
    return results
```

### Automated Remediation Rules

```python
AUTOMATED_REMEDIATION_RULES = {
    'subnet_ip_exhaustion': {
        'condition': "SubnetAvailableIPs < 10",
        'action': 'create_new_subnet',
        'parameters': {
            'expansion_size': 'next_available_cidr',
            'copy_configuration': True,
            'notify': True
        },
        'approval_required': False
    },
    'vpc_peering_failed': {
        'condition': "VPCPeeringConnectionStatus != 'active' for 15min",
        'action': 'recreate_peering',
        'parameters': {
            'max_attempts': 3,
            'fallback_to_vpn': True,
            'notify': True
        },
        'approval_required': True
    },
    'high_packet_loss': {
        'condition': "VPCPacketLossRate > 10% for 10min",
        'action': 'reroute_traffic',
        'parameters': {
            'alternative_az': True,
            'update_route_tables': True,
            'notify': True
        },
        'approval_required': False
    }
}
```

## Reporting and Notifications

### Daily Report Template
```python
def generate_vpc_daily_report(client, vpc_ids):
    """
    Generate daily VPC health and performance report.
    
    Args:
        client: CtyunClient instance
        vpc_ids: List of VPC IDs
    
    Returns:
        str: Markdown formatted report
    """
    health_results = daily_vpc_health_check(client, vpc_ids)
    
    report = "# VPC Daily Health Report\n\n"
    report += f"**Report Date**: {datetime.now().strftime('%Y-%m-%d')}\n"
    report += f"**Total VPCs**: {len(vpc_ids)}\n\n"
    
    # Summary
    status_counts = {}
    for vpc_id, result in health_results.items():
        status = result['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    report += "## Summary\n"
    for status, count in sorted(status_counts.items()):
        report += f"- **{status}**: {count} VPCs\n"
    report += "\n"
    
    # Detailed findings
    report += "## Detailed Findings\n"
    for vpc_id, result in health_results.items():
        if result['status'] != 'HEALTHY':
            report += f"### {vpc_id} - {result['status']}\n"
            report += f"- Checked at: {result['timestamp']}\n"
            for issue in result.get('issues', []):
                report += f"  - {issue}\n"
            if 'metrics' in result:
                for metric, value in result['metrics'].items():
                    report += f"  - {metric}: {value}\n"
            report += "\n"
    
    # Recommendations
    report += "## Recommendations\n"
    
    # Check for subnet capacity issues
    capacity_issues = []
    for vpc_id, result in health_results.items():
        if 'full_subnets' in result.get('metrics', {}):
            for subnet in result['metrics']['full_subnets']:
                capacity_issues.append({
                    'vpc': vpc_id,
                    'subnet': subnet['subnet_id'],
                    'utilization': subnet['utilization']
                })
    
    if capacity_issues:
        report += "### Capacity Planning Needed\n"
        for issue in capacity_issues:
            report += (
                f"- VPC {issue['vpc']}, Subnet {issue['subnet']}: "
                f"{issue['utilization']:.1f}% utilized\n"
            )
        report += "\n"
    
    # Check for peering issues
    peering_issues = []
    for vpc_id, result in health_results.items():
        if any('peering' in issue.lower() for issue in result.get('issues', [])):
            peering_issues.append(vpc_id)
    
    if peering_issues:
        report += "### Peering Connection Issues\n"
        for vpc_id in peering_issues:
            report += f"- VPC {vpc_id} has peering connection issues\n"
        report += "\n"
    
    report += "---\n"
    report += "*Report generated automatically by VPC Monitoring System*\n"
    
    return report
```

### Notification Channels

| Severity | Notification Channel | Response Time SLA |
|---|---|---|
| **Critical (P0)** | SMS + Phone Call + PagerDuty | < 15 minutes |
| **High (P1)** | Email + Slack + PagerDuty | < 1 hour |
| **Medium (P2)** | Email + Slack | < 4 hours |
| **Low (P3)** | Weekly digest email | < 24 hours |

## Version History

| Version | Date | Change |
|---|---|---|
| v1 | 2026-06-05 | Initial VPC monitoring guide |