# How to manage kubernetes within kubernetes in GCP

In this ropository we will see the steps to follow and good practices to use the python client for the kubernetes API within Kubernetes itself and how to use RBAC authorization in the Google Cloud platform

## First step
We create an example application with its own environment, dockerize it and upload it to the artifact registry

```bash
python -m venv venv
```
```bash
pip install kubernetes
```
```bash
pip freeze > requirements.txt
```

For this example we make a simple script that lists the pods in a specific namespace
```python
from kubernetes import client, config

config.load_incluster_config()
v1 = client.CoreV1Api()

namespace = 'NAMESPACE_NAME'
pods = v1.list_namespaced_pod(namespace)   

print("Pods en el namespace '%s':" % namespace)
for pod in pods.items:
    print("%s\t%s\t%s" % (pod.metadata.name, pod.status.phase, pod.status.pod_ip))
```
Create a dockerfile
```docker
FROM python:3.9.19-bookworm

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
```
Build it
```bash
docker build -t gcr.io/PROJECT_ID/example-docker-image:0.0.1 .
```
Push it to the artifact registry
```bash
docker push gcr.io/PROJECT_ID/example-docker-image:0.0.1
```

## Second step
Create a kubernetes cluster and manage it from kubectl, create a namespace

```bash
gcloud container clusters get-credentials CLUSTER_NAME --region CLUSTER_REGION --project PROJECT_ID
```
Create a namespace
```bash
kubectl create namespace NAMESPACE_NAME
```
Create a kubernetes service account in the namespace created above
```bash
kubectl create serviceaccount KSA_NAME \
    --namespace NAMESPACE_NAME
```
## Third step
Grant the necessary roles to the kubernetes service account and link them with rbac

Create the role you want, in this case we will simply list pods
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: NAMESPACE_NAME
  name: list-pods-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["list"]
```

```bash
kubectl apply -f PATH_TO_ROLE.YAML -n NAMESPACE_NAME
```

Bind the role to the service account
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: list-pods-binding
  namespace: NAMESPACE_NAME
subjects:
- kind: ServiceAccount
  name: KSA_NAME
  namespace: NAMESPACE_NAME
roleRef:
  kind: Role
  name: list-pods-role
  apiGroup: rbac.authorization.k8s.io

```

```bash
kubectl apply -f PATH_TO_ROLEBINDING.YAML -n NAMESPACE_NAME
```

## Last step
Create a manifest for the pod that lists pods, assign the variables, apply it and exec it

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: podexample
spec:
  serviceAccountName: KSA_NAME
  containers:
  - name: example-container
    image: example-docker-image:0.0.1
    command: ["sleep","infinity"]
```

```bash
kubectl apply -f PATH_TO_PODEXAMPLE.YAML -n NAMESPACE_NAME
```

```bash
kubectl get pods -n NAMESPACE_NAME
```

```bash
kubectl exec -ti podexample -n NAMESPACE_NAME -- bash
```

Inside the container run the script to list the pods
```bash
python example.py
```
## For more information consult the official documentation
https://kubernetes.io/docs/reference/access-authn-authz/rbac/