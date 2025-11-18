from mangum import Mangum
from app.main import app
import sys, os, time

print("=== handler.py: Lambda image started ===")
print("PYTHONPATH =", sys.path)
print("Working directory =", os.getcwd())
time.sleep(0.2)

lambda_handler = Mangum(app)
print("=== handler.py: Mangum handler initialized successfully ===")

