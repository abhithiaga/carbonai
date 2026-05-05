"""
AWS Lambda handler — wraps FastAPI app with Mangum.
Deploy via serverless.yml or SAM template.yaml.
"""
from mangum import Mangum
from app.main import app

handler = Mangum(app, lifespan="off")
