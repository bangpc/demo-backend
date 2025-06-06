# demo-backend

## Infrastructure

The project uses AWS CDK with Python to define the cloud infrastructure. The stack includes:
- Lambda function
- API Gateway

## Setup

1. Install Python dependencies:
```bash
cd cdk
pip install -r requirements.txt
```

## Local Development

1. Install development dependencies:
```bash
cd cdk
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
python -m pytest
```

3. Test CDK synthesis locally:
```bash
cdk synth
```

4. Local deployment for testing:
```bash
cdk deploy --profile local
```

5. Cleanup after testing:
```bash
cdk destroy --profile local
```

## Testing

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Run API tests:
```bash
pytest tests/test_main.py -v
```

3. Run infrastructure tests:
```bash
cdk
pytest tests/test_stack.py -v
```

4. Run all tests with coverage:
```bash
pytest --cov=. tests/
```

## Deployment

This project uses GitHub Actions for automated deployment to AWS using CDK. To set up deployments:

1. Add the following secrets to your GitHub repository:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`

2. Push changes to the main/master branch to trigger automatic deployment.

3. Monitor the deployment in the Actions tab of your GitHub repository.