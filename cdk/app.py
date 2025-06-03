#!/usr/bin/env python3
from aws_cdk import App, Stack, Environment
from constructs import Construct
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
import os

class DemoBackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        vpc = ec2.Vpc(self, "DemoVPC", max_azs=2)

        # Security Group for EC2
        ec2_sg = ec2.SecurityGroup(
            self, "DemoEC2SecurityGroup",
            vpc=vpc,
            allow_all_outbound=True
        )
        ec2_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP")
        ec2_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH")

        # IAM Role for EC2 with CloudWatch logging permissions
        ec2_role = iam.Role(
            self, "DemoEC2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy"),
            ]
        )

        # UserData script to install Docker and run your image, and install CloudWatch agent
        dockerhub_username = os.getenv("DOCKERHUB_USERNAME", "")
        image_name = f"{dockerhub_username}/demo-backend-stg:latest"
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "yum update -y",
            "amazon-linux-extras install docker -y",
            "service docker start",
            "usermod -a -G docker ec2-user",
            # Install CloudWatch agent
            "yum install -y amazon-cloudwatch-agent",
            # Create CloudWatch agent config file
            "cat <<EOF > /opt/aws/amazon-cloudwatch-agent/bin/config.json",
            '{',
            '  "logs": {',
            '    "logs_collected": {',
            '      "files": {',
            '        "collect_list": [',
            '          {',
            '            "file_path": "/var/log/messages",',
            '            "log_group_name": "/ec2/demo-backend/messages",',
            '            "log_stream_name": "{instance_id}"',
            '          },',
            '          {',
            '            "file_path": "/var/log/cloud-init.log",',
            '            "log_group_name": "/ec2/demo-backend/cloud-init",',
            '            "log_stream_name": "{instance_id}"',
            '          }',
            '        ]',
            '      }',
            '    }',
            '  }',
            '}',
            "EOF",
            # Start CloudWatch agent
            "/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json -s",
            # Docker login and run
            f"docker login -u {dockerhub_username} -p $(aws ssm get-parameter --name /dockerhub/password --with-decryption --query Parameter.Value --output text --region {os.getenv('CDK_DEFAULT_REGION', 'us-east-1')})",
            f"docker pull {image_name}",
            f"docker run -d -p 80:80 {image_name}"
        )

        # EC2 Instance
        ec2.Instance(
            self, "DemoBackendEC2",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=vpc,
            security_group=ec2_sg,
            user_data=user_data,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            # key_name=os.getenv("EC2_KEY_NAME"),  # Optional: for SSH access
            associate_public_ip_address=True,
            role=ec2_role
        )

def create_stack(app, stack_name, env, tags):
    DemoBackendStack(
        app, stack_name,
        env=env,
        tags=tags
    )

app = App()

# For production
prod_env = Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION')
)
prod_tags = {
    'environment': 'production',
    'requires-approval': 'true'
}
create_stack(app, "DemoBackendStackProd", prod_env, prod_tags)

# For testing
test_env = Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION')
)
test_tags = {
    'environment': 'test',
    'requires-approval': 'false'
}
create_stack(app, "DemoBackendStackTest", test_env, test_tags)

app.synth()
