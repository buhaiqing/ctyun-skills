# CTyun VPC Core Concepts

## Overview
Virtual Private Cloud (VPC) is a logically isolated network space within CTyun. This document covers VPC architecture, components, and operational concepts.

## VPC Architecture

### Key Components

| Component | Description | Key Attributes |
|---|---|---|
| **VPC** | Isolated virtual network | CIDR block, region, tenancy (default/dedicated) |
| **Subnet** | Subdivision of VCIDR | CIDR block, availability zone, route table association |
| **Route Table** | Routing rules for subnet traffic | Routes (destination → target), associations |
| **Internet Gateway** | Internet access for VPC | Attached to VPC, routes 0.0.0.0/0 traffic |
| **NAT Gateway** | Outbound internet for private subnets | Elastic IP, subnet association |
| **VPC Peering** | Connection between two VPCs | Requester VPC, accepter VPC, status (pending/active) |
| **Network ACL** | Stateless firewall at subnet level | Inbound/outbound rules, rule numbers (1-32766) |
| **Security Group** | Stateful firewall at instance level | Inbound/outbound rules (EC2-level, not VPC) |

### CIDR Block Management

#### Private IP Ranges (RFC 1918)
- `10.0.0.0/8` (10.0.0.0 - 10.255.255.255) - 16,777,214 addresses
- `172.16.0.0/12` (172.16.0.0 - 172.31.255.255) - 1,048,574 addresses  
- `192.168.0.0/16` (192.168.0.0 - 192.168.255.255) - 65,534 addresses

#### CIDR Sizing Guidelines
- **VPC CIDR**: `/16` to `/28` (recommended `/16` for large deployments)
- **Subnet CIDR**: Must be within VPC CIDR, `/16` to `/28` (minimum `/28`)
- **Reserved addresses**: First 4 and last 1 addresses in each subnet are reserved

### VPC Limits and Quotas

| Resource | Default Limit | Adjustable |
|---|---|---|
| VPCs per region | 5 | Yes |
| Subnets per VPC | 200 | Yes |
| Route tables per VPC | 200 | Yes |
| Routes per route table | 50 | Yes |
| Network ACLs per VPC | 200 | Yes |
| Rules per network ACL | 20 (inbound) + 20 (outbound) | No |
| VPC peering connections | 50 | Yes |
| IPv4 CIDR blocks per VPC | 5 | Yes |

## Network Topology Patterns

### Single-Tier Architecture
```
VPC (10.0.0.0/16)
├── Public Subnet (10.0.1.0/24) - AZ A
│   ├── Route to Internet Gateway
│   └── Web servers with public IPs
└── Private Subnet (10.0.2.0/24) - AZ A
    ├── Route to NAT Gateway
    └── Application servers
```

### Multi-Tier Architecture  
```
VPC (10.0.0.0/16)
├── Web Tier (10.0.1.0/24) - Public
│   └── Internet Gateway route
├── App Tier (10.0.2.0/24) - Private
│   └── NAT Gateway route
└── Data Tier (10.0.3.0/24) - Private
    └── No internet route (isolated)
```

### Multi-AZ High Availability
```
VPC (10.0.0.0/16)
├── AZ A
│   ├── Public Subnet (10.0.1.0/24)
│   └── Private Subnet (10.0.2.0/24)
├── AZ B  
│   ├── Public Subnet (10.0.3.0/24)
│   └── Private Subnet (10.0.4.0/24)
└── AZ C
    ├── Public Subnet (10.0.5.0/24)
    └── Private Subnet (10.0.6.0/24)
```

## Routing and Connectivity

### Route Table Basics
- Each VPC has a **main route table** (cannot be deleted)
- Subnets can be associated with custom route tables
- Routes have priority based on prefix length (longest match)

### Route Targets
| Target Type | Description | Use Case |
|---|---|---|
| `local` | VPC-local traffic | Always present for VPC CIDR |
| `igw-*` | Internet Gateway | Public internet access |
| `nat-*` | NAT Gateway | Private subnet outbound internet |
| `pcx-*` | VPC Peering Connection | Cross-VPC traffic |
| `eni-*` | Elastic Network Interface | Instance-specific routing |
| `vpce-*` | VPC Endpoint | Private service access |

### VPC Peering Rules
1. **No transitive routing**: Peering is not transitive (A↔B and B↔C does not give A↔C)
2. **No overlapping CIDRs**: Peered VPCs must not have overlapping IP ranges
3. **Cross-account support**: Peering can be between VPCs in different accounts
4. **Cross-region support**: Some regions support inter-region VPC peering

## Security and Access Control

### Network ACLs vs Security Groups

| Aspect | Network ACL | Security Group |
|---|---|---|
| **Level** | Subnet level | Instance level |
| **Stateful** | No (stateless) | Yes (stateful) |
| **Rule evaluation** | Rule number order (lowest first) | All rules evaluated |
| **Default behavior** | Deny all (explicit allow needed) | Deny all (explicit allow needed) |
| **Rule types** | Allow/Deny | Allow only |

### Recommended Security Practices

#### Network ACL Best Practices
1. **Start with deny-all**: Default network ACL denies all inbound/outbound
2. **Ephemeral ports**: Allow outbound ephemeral ports (1024-65535) for responses
3. **Rule numbering**: Use increments of 100 (100, 200, 300) for easy insertion
4. **Logging**: Enable VPC Flow Logs for network ACL traffic

#### VPC Flow Logs
- Capture IP traffic information
- Can be published to CloudWatch Logs or S3
- Useful for security monitoring and troubleshooting
- Enable per VPC, subnet, or network interface

## Operational Considerations

### VPC Creation Best Practices
1. **Plan CIDR carefully**: Choose CIDR that won't overlap with other networks (corporate, other VPCs)
2. **Reserve space for growth**: Start with /16 even if small, allows room for expansion
3. **Consider multi-region**: If multi-region deployment planned, ensure non-overlapping CIDRs
4. **Tag consistently**: Use tags for cost allocation and resource management

### Subnet Design
1. **Size for growth**: Allocate /24 subnets even if starting small
2. **AZ distribution**: Distribute subnets across availability zones for HA
3. **Tier separation**: Separate public, private, and data tiers into different subnets
4. **Route table associations**: Associate subnets with appropriate route tables

### Deletion Dependencies
Resources that must be deleted **before** VPC deletion:
1. **Internet Gateway** (detach from VPC)
2. **NAT Gateways** (delete)
3. **VPC Endpoints** (delete)
4. **VPC Peering Connections** (delete/reject)
5. **Network ACLs** (except default)
6. **Route Tables** (except main)
7. **Subnets** (must be empty)
8. **Security Groups** (if not used elsewhere)

### Monitoring and Troubleshooting

#### Key Metrics to Monitor
- **VPCPeeringConnectionStatus**: Peering connection health
- **VPCBandwidth**: Network throughput
- **VPCPacketLoss**: Packet loss percentage
- **VPCConnections**: Active connections

#### Common Issues and Solutions

| Issue | Symptoms | Solution |
|---|---|---|
| **CIDR conflict** | VPC creation fails | Choose non-overlapping CIDR |
| **Subnet full** | Cannot launch instances | Create new subnet or resize |
| **Routing loop** | Traffic blackholed | Check route table for circular routes |
| **Peering failure** | Cross-VPC traffic blocked | Verify peering acceptance and route propagation |
| **Security misconfiguration** | Connectivity issues | Check both network ACLs and security groups |

## Integration with Other CTyun Services

### ECS Integration
- ECS instances launch into subnets
- Security groups control instance-level traffic
- Elastic Network Interfaces (ENIs) attach to instances

### ELB Integration
- Load balancers require subnets in multiple AZs
- Internet-facing vs internal load balancers
- Security groups for load balancer traffic

### RDS Integration
- RDS instances deploy into subnets
- Database security groups control access
- Multi-AZ deployments across subnet AZs

### VPN/Direct Connect
- Virtual Private Gateway (VGW) attaches to VPC
- Customer Gateway connects on-premises
- VPN tunnels or Direct Connect for hybrid cloud

## Version History

| Version | Date | Change |
|---|---|---|
| v1 | 2026-06-05 | Initial VPC core concepts document |