# demo-backend

## Infrastructure

The project uses AWS CDK with Python to define the cloud infrastructure. The stack includes:
- Lambda function
- API Gateway

### Infrastructure Testing

Infrastructure tests for the CDK stack are located in `tests/test_stack.py`. These tests verify that key AWS resources (such as VPC and ALB) are present in the synthesized CloudFormation template.

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
pytest tests/test_stack.py -v
```

4. Run all tests with coverage:
```bash
pytest --cov=. tests/
```

### Development Testing Workflow

The project includes a GitHub Actions workflow for testing code in development:

- Triggers on push to `dev` and `feature/*` branches
- Triggers on pull requests to `dev` branch
- Sets up Python and MongoDB environment
- Runs all tests with coverage reporting
- Uploads coverage reports to Codecov

Required repository secrets for dev testing:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `AWS_S3_BUCKET`
- `CODECOV_TOKEN` (for coverage reporting)

## Deployment

This project uses GitHub Actions for automated deployment to AWS using CDK. To set up deployments:

1. Add the following secrets to your GitHub repository:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`

2. Push changes to the main/master branch to trigger automatic deployment.

### Manual CDK Deployment

You can deploy to different environments using the following commands:

**Test environment:**
```bash
cd cdk
python app_test.py
```

**Production environment:**
```bash
cd cdk
python app_prod.py
```

## Docker Configuration

To deploy and run the backend Docker image, you need to provide your Docker Hub credentials and AWS region:

- **DOCKERHUB_USERNAME**: Your Docker Hub username.
- **DOCKERHUB_PASSWORD** or **DOCKERHUB_TOKEN**: Your Docker Hub password or access token.
- **AWS_REGION**: The AWS region for deployment.

### Local Development

Set these as environment variables in your shell or in a `.env` file at the project root:

```bash
export DOCKERHUB_USERNAME=your_dockerhub_username
export DOCKERHUB_PASSWORD=your_dockerhub_password
export AWS_REGION=us-east-1
```

Or create a `.env` file:

```
DOCKERHUB_USERNAME=your_dockerhub_username
DOCKERHUB_PASSWORD=your_dockerhub_password
AWS_REGION=us-east-1
```

### CI/CD (GitHub Actions)

In GitHub Actions workflows, these values should be set as repository secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN` (recommended over password)
- `AWS_REGION`

These secrets are referenced in the workflow YAML files and passed as environment variables to the deployment scripts.