from kubernetes import client, config

config.load_incluster_config()
v1 = client.CoreV1Api()

namespace = 'NAMESPACE_NAME'
pods = v1.list_namespaced_pod(namespace)   

print("Pods in the namespace '%s':" % namespace)
for pod in pods.items:
    print("%s\t%s\t%s" % (pod.metadata.name, pod.status.phase, pod.status.pod_ip))
