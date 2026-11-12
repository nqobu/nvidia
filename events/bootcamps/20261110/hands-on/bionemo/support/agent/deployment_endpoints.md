# Self-study NIM endpoints

Read `support.workshop.ENDPOINTS`; defaults use the host loopback ports in compose.yaml.
GENMOL_URL, DIFFDOCK_URL and BOLTZ2_URL override the complete prediction URLs.
The agent must honor these endpoints rather than deploying a second model stack.
Readiness: GET http://127.0.0.1:8001/v1/health/ready (and ports 8002, 8003).
Scientific request payloads and the single-candidate guard remain in workshop.py.
