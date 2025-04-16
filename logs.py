import subprocess
from flask import Flask, render_template, request
import os

# Specify the custom template folder
app = Flask(__name__, template_folder='views')

def get_pods():
    """Fetches a list of Kubernetes pods using kubectl."""
    result = subprocess.run(["kubectl", "get", "pods", "--no-headers", "-o", "custom-columns=NAME:.metadata.name"], stdout=subprocess.PIPE)
    pods = result.stdout.decode("utf-8").strip().split("\n")
    return pods

def get_pod_logs(pod_name):
    """Fetches logs for a given pod."""
    result = subprocess.run(["kubectl", "logs", pod_name], stdout=subprocess.PIPE)
    logs = result.stdout.decode("utf-8")
    return logs

@app.route('/')
def index():
    """Main page that lists pods."""
    pods = get_pods()
    return render_template('index.html', pods=pods)

@app.route('/logs', methods=['POST'])
def logs():
    """Shows logs for a selected pod."""
    pod_name = request.form.get('pod_name')
    logs = get_pod_logs(pod_name)
    return render_template('index.html', logs=logs, pods=get_pods(), selected_pod=pod_name)

if __name__ == '__main__':
    app.run(debug=True)
