
from kubernetes import client, config

config.load_kube_config()

v1 = client.CoreV1Api()

for pod in v1.list_pod_for_all_namespaces().items:
    if pod.status.phase != "Running":
        print("ALERT:", pod.metadata.name)
        
    if pod.status.container_statuses:
    for c in pod.status.container_statuses:
        if c.restart_count > 3:
            print("ALERT: Restart loop detected:", pod.metadata.name)
