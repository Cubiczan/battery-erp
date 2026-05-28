"""AWS Lambda entry point using Mangum adapter for FastAPI."""

from mangum import Mangum

from battery_erp.app.main import app

handler = Mangum(app, lifespan="off")
