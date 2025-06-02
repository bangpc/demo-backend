from aws_cdk import App, Environment
import os
from app import create_stack

app = App()
create_stack(
    app,
    "DemoBackendStackProd",
    env=Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    ),
    tags={
        'environment': 'production',
        'requires-approval': 'true'
    }
)
app.synth()
