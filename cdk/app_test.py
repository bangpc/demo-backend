from aws_cdk import App, Environment
import os
from app import create_stack

app = App()
create_stack(
    app,
    "DemoBackendStackTest",
    env=Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    ),
    tags={
        'environment': 'test',
        'requires-approval': 'false'
    }
)
app.synth()