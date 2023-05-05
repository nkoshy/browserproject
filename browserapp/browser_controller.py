import yaml
from kubernetes.client import V1DeleteOptions
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes import client, config

# Read the token, CA certificate, and namespace from files
#with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as f:
#    token = f.read()
#with open("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt", "r") as f:
#    ca_cert = f.read()
#with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
#    namespace = f.read()


# Set the API key
apikey = "abcabcabcabcabcabc"
#browsermaxcount = 10
#configuration = client.Configuration()
#configuration.host = "https://kubernetes.default.svc"  # Default API server address within a cluster
#configuration.ssl_ca_cert = ca_cert
#configuration.api_key = {"authorization": "Bearer " + token}
#configuration.api_key_prefix = {"authorization": "Bearer"}

# Initialize the API client with the custom configuration
#client.Configuration.set_default(configuration)

# Configure the Kubernetes client
#config.load_kube_config()
config.load_incluster_config()

# Create instances of the required clients
api_instance = client.CoreV1Api()
apps_v1 = client.AppsV1Api()
networking_v1 = client.NetworkingV1Api()

def count_deployments_with_name_ending(ending):

    namespaces = api_instance.CoreV1Api().list_namespace()
    count = 0

    for ns in namespaces.items:
        deployments = apps_v1.list_namespaced_deployment(ns.metadata.name)
        for dep in deployments.items:
            if dep.metadata.name.endswith(ending):
                count += 1

    return count

def create_namespace(name):
    namespace = client.V1Namespace(
        metadata=client.V1ObjectMeta(name=name)
    )
    try:
        api_instance.create_namespace(namespace)
    except ApiException as e:
        if e.status != 409:  # Ignore "AlreadyExists" errors
            raise

def create_deployment(name, namespace):
    deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: firefox-vnc
  name: firefox-vnc
  namespace: default
spec:
  progressDeadlineSeconds: 600
  replicas: 1
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      app: firefox-vnc
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: firefox-vnc
    spec:
      containers:
      - image: jlesage/firefox
        imagePullPolicy: Always
        name: firefox
        ports:
        - containerPort: 5800
          protocol: TCP
        resources: {}
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
        volumeMounts:
        - mountPath: /config
          name: firefox-storage
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext: {}
      terminationGracePeriodSeconds: 30
      volumes:
      - emptyDir: {}
        name: firefox-storage
       """
    dep = yaml.safe_load(deployment)
    dep['metadata']['name'] = f'{name}-firefoxvnc'
    dep['metadata']['namespace'] = namespace
    dep['metadata']['labels']['app'] = name
    dep['spec']['selector']['matchLabels']['app'] = name
    dep['spec']['template']['metadata']['labels']['app'] = name
    try:
        apps_v1.create_namespaced_deployment(namespace, dep)
    except ApiException as e:
        if e.status != 409:  # Ignore "AlreadyExists" errors
            raise

def create_service(name, namespace):
    service = """
apiVersion: v1
kind: Service
metadata:
  name: firefox-vnc-service
  namespace: default
spec:
  ports:
  - port: 5800
    protocol: TCP
    targetPort: 5800
  selector:
    app: firefox-vnc
  type: ClusterIP
    """
    svc = yaml.safe_load(service)
    svc['metadata']['name'] = f'{name}-firefoxvnc'
    svc['metadata']['namespace'] = namespace
    svc['spec']['selector']['app'] = name
    try:
        api_instance.create_namespaced_service(namespace, svc)
    except ApiException as e:
        if e.status != 409:  # Ignore "AlreadyExists" errors
            raise

def create_ingress(name, namespace):
    ingress = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubernets.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/ssl-passthrough: "false"
    nginx.ingress.kubernetes.io/ssl-ciphers: "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:!DSS"
    nginx.ingress.kubernetes.io/ssl-protocols: "TLSv1.2,TLSv1.3"
  name: firefoxvnc-ingress
  namespace: default
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - rbidemo.ssosec.com
      secretName: my-tls-secret
  rules:
  - host: rbidemo.ssosec.com
    http:
      paths:
      - backend:
          service:
            name: firefox-vnc-service
            port:
              number: 5800
        pathType: Prefix
        path: /niju(/|$)(.*)
    """
    ing = yaml.safe_load(ingress)
    ing['metadata']['name'] = f'{name}-firefoxvnc'
    ing['metadata']['namespace'] = namespace
    ing['spec']['rules'][0]['http']['paths'][0]['backend']['service']['name'] = f'{name}-firefoxvnc'
    ing['spec']['rules'][0]['http']['paths'][0]['path'] = f"/{namespace}/{name}(/|$)(.*)"
    try:
        networking_v1.create_namespaced_ingress(namespace, ing)
    except ApiException as e:
        if e.status != 409:  # Ignore "AlreadyExists" errors
            raise

def create_browser(realm, username, apikey):
    if apikey != apikey:
        return {"status": 401, "message": "authentication failure"}

    #count = count_deployments_with_name_ending('-firefoxvnc')

    #if count >= browsermaxcount:
    #    return {"status": 401, "message": "system capacity execeeded"}

    try:
        create_namespace(realm)
        create_deployment(f"{username}", realm)
        create_service(f"{username}", realm)
        create_ingress(f"{username}", realm)
        return {"url": f"http://fortifybrowser.ssosec.test:32276/{realm}/{username}/", "status": 200}
    except ApiException as e:
        return {"status": 503, "message": str(e)}

def get_browser_status(realm, username, apikey):
    if apikey != apikey:
        return {"status": 401, "message": "authentication failure"}

    try:
        deployment_name = f"{username}-firefoxvnc"
        response = apps_v1.read_namespaced_deployment_status(deployment_name, realm)
        pod_status = response.status.conditions[-1].type

        pod = None
        for i in client.CoreV1Api().list_namespaced_pod(realm).items:
            if deployment_name in i.metadata.name:
                pod = i
                break

        creation_time = pod.metadata.creation_timestamp

        return {"status": 200, "deployment_name": deployment_name, "status": pod_status, "creation_time": creation_time}
    except ApiException as e:
        return {"status": 500, "message": str(e)}

def get_realm_browsers(realm, apikey):
    if apikey != apikey:
        return {"status": 401, "message": "authentication failure"}

    try:
        deployments = apps_v1.list_namespaced_deployment(realm)
        deployment_list = []
        for deployment in deployments.items:
            deployment_name = deployment.metadata.name
            pod_status = deployment.status.conditions[-1].type
            creation_time = deployment.metadata.creation_timestamp
            deployment_list.append({"deployment_name": deployment_name, "status": pod_status, "creation_time": creation_time})

        return {"status": 200, "deployments": deployment_list}
    except ApiException as e:
        return {"status": 500, "message": str(e)}

def delete_browser(realm, username, apikey):
    if apikey != apikey:
        return {"status": 401, "message": "authentication failure"}

    try:
        deployment_name = f"{username}-firefoxvnc"

        # Delete deployment
        apps_v1.delete_namespaced_deployment(deployment_name, realm)

        # Delete service
        api_instance.delete_namespaced_service(deployment_name, realm)

        # Delete ingress
        networking_v1.delete_namespaced_ingress(deployment_name, realm, body=V1DeleteOptions())


        apps_v1.delete_namespaced_deployment(deployment_name, realm)
        return {"status": 200}
    except ApiException as e:
        if e.status == 404:  # Ignore "NotFound" errors
            return {"status": 200}
        return {"status": 500, "message": str(e)}

def delete_realm(realm, apikey):
    if apikey != apikey:
        return {"status": 401, "message": "authentication failure"}

    try:
        # Delete all deployments in the namespace
        deployments = apps_v1.list_namespaced_deployment(realm)
        for deployment in deployments.items:
            apps_v1.delete_namespaced_deployment(deployment.metadata.name, realm)

        # Delete all services in the namespace
        services = api_instance.list_namespaced_service(realm)
        for service in services.items:
            api_instance.delete_namespaced_service(service.metadata.name, realm)

        # Delete all ingresses in the namespace
        ingresses = networking_v1.list_namespaced_ingress(realm)
        for ingress in ingresses.items:
            networking_v1.delete_namespaced_ingress(ingress.metadata.name, realm, body=V1DeleteOptions())

        # Delete the namespace
        #api_instance = client.CoreV1Api()
        api_instance.delete_namespace(realm)

        return {"status": 200}
    except ApiException as e:
        if e.status == 404:  # Ignore "NotFound" errors
            return {"status": 200}
        return {"status": 500, "message": str(e)}

