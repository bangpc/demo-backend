#!/usr/bin/env python3
from aws_cdk import App, Stack
from constructs import Construct
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_autoscaling as autoscaling
from aws_cdk import Duration

class DemoBackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        vpc = ec2.Vpc(self, "DemoVPC",
            max_azs=2
        )

        # Create Security Group
        security_group = ec2.SecurityGroup(
            self, "DemoSecurityGroup",
            vpc=vpc,
            allow_all_outbound=True
        )
        # Allow HTTP traffic
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP"
        )
        # Allow HTTPS traffic
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443),
            "Allow HTTPS"
        )

        # Create ALB Security Group
        alb_security_group = ec2.SecurityGroup(
            self, "DemoALBSecurityGroup",
            vpc=vpc,
            allow_all_outbound=True
        )
        alb_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP ALB"
        )
        alb_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443),
            "Allow HTTPS ALB"
        )

        # Create Auto Scaling Group
        asg = autoscaling.AutoScalingGroup(
            self, "DemoASG",
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.AmazonLinuxImage(),
            min_capacity=1,
            max_capacity=3,
            security_group=security_group
        )

        # Create Application Load Balancer with security group
        alb = elbv2.ApplicationLoadBalancer(
            self, "DemoALB",
            vpc=vpc,
            internet_facing=True,
            security_group=alb_security_group
        )

        # Add both HTTP and HTTPS listeners
        http_listener = alb.add_listener("HTTPListener", port=80)
        http_listener.add_targets("Target",
            port=80,
            targets=[asg],
            health_check=elbv2.HealthCheck(
                path="/health",
                healthy_http_codes="200",
                interval=Duration.seconds(30)
            )
        )

app = App()
DemoBackendStack(app, "DemoBackendStack")
app.synth()
