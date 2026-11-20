"""Flask application with OpenTelemetry instrumentation."""

import time
from flask import Flask, jsonify, request
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.metrics import get_meter_provider, set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

app = Flask(__name__)

# OTel Setup
trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

FlaskInstrumentor().instrument_app(app)

# Metrics setup
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="otel-collector:4317", insecure=True), export_interval_millis=5000)
meter_provider = MeterProvider(metric_readers=[metric_reader])
set_meter_provider(meter_provider)

meter = get_meter_provider().get_meter(__name__)

# Request counter and latency histogram
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total number of HTTP requests",
    unit="1"
)

latency_histogram = meter.create_histogram(
    name="http_request_duration_seconds",
    description="Duration of HTTP requests",
    unit="s"
)

@app.before_request
def before_request():
    """Record start time for latency tracking."""
    request.start_time = time.time()

@app.after_request
def after_request(response):
    """Update metrics on request completion."""
    duration = time.time() - getattr(request, 'start_time', time.time())
    latency_histogram.record(duration, {
        "method": request.method,
        "path": request.path,
        "status": response.status_code
    })
    request_counter.add(1, {
        "method": request.method,
        "path": request.path,
        "status": response.status_code
    })
    return response

tracer = trace.get_tracer(__name__)

@app.route('/healthz')
def healthz():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def index():
    """Root endpoint."""
    with tracer.start_as_current_span("index-handler"):
        return jsonify({"message": "Welcome to the observability demo"}), 200

@app.route('/slow')
def slow():
    """Simulates a slow operation."""
    with tracer.start_as_current_span("slow-handler"):
        time.sleep(1.5)
        return jsonify({"message": "Slow response complete"}), 200

@app.route('/error')
def error():
    """Simulates an error response."""
    with tracer.start_as_current_span("error-handler"):
        raise RuntimeError("Simulated error for testing")

@app.route('/chain')
def chain():
    """Creates nested spans to demonstrate distributed tracing."""
    with tracer.start_as_current_span("chain-handler"):
        result = process_step_1()
        result = process_step_2(result)
        result = process_step_3(result)
        return jsonify({"message": "Chain complete", "result": result}), 200

def process_step_1():
    """First processing step."""
    with tracer.start_as_current_span("process-step-1"):
        time.sleep(0.1)
        return "step1"

def process_step_2(step1_result):
    """Second processing step."""
    with tracer.start_as_current_span("process-step-2"):
        time.sleep(0.2)
        return f"{step1_result}->step2"

def process_step_3(step2_result):
    """Third processing step."""
    with tracer.start_as_current_span("process-step-3"):
        time.sleep(0.15)
        return f"{step2_result}->step3"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
