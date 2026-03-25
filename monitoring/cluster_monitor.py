
from kubernetes import client, config

config.load_kube_config()

v1 = client.CoreV1Api()

for pod in v1.list_pod_for_all_namespaces().items:
    if pod.status.phase != "Running":
        print("ALERT:", pod.metadata.name)
