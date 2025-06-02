import pytest
from aws_cdk import App
from cdk.app import DemoBackendStack

def test_stack_synthesizes():
    app = App()
    stack = DemoBackendStack(app, "TestStack")
    template = app.synth().get_stack_by_name("TestStack").template
    # Check that VPC and ALB are present in the template
    resources = template.get("Resources", {})
    vpc = [r for r in resources.values() if r["Type"] == "AWS::EC2::VPC"]
    alb = [r for r in resources.values() if r["Type"] == "AWS::ElasticLoadBalancingV2::LoadBalancer"]
    assert vpc, "VPC resource not found in template"
    assert alb, "ALB resource not found in template"
