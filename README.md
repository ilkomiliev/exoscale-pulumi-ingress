# Exoscale SKS Pulumi

This repo provisions an Exoscale SKS cluster, using Pulumi, installs the nginx ingress controller and provisions two services, using NLB 
and the ingress definitions under two different hostnames: `app1.demo` and `app2.demo`.

Limitations: 
- the apps are in a single namespace, setting cross-namespace ingress is more complicated and left out of scope.
- this is just a demo and not production ready setup!

## Python

You need python virtual environment: you can set one by executing `python venv venv`

Activate the venv and install the pip packages:

```bash
(venv) $ pip install -r requirements.txt
```

## Pulumi Config

```bash
pulumi config set exoscale:key <your exoscale API key>
pulumi config set exoscale:secret --secret <your exoscale API key secret>
```

## Demo app

There are no checks at the moment for the real status of the pods, that's why there are manual steps necessary.

```bash
./set-all.sh
```
shows by default (without parameters) all the kubernetes objects in all namespaces. It can be used anytime to check the status.

### Install the SKS cluster

To setup the whole SKS stack, simply execute:

```bash
./set-all.sh sks
```

> Check the status until all the pods are in status `Running`, before continue with the next step:

```
$ ./set-all.sh
List all kubernetes resources
NAMESPACE     NAME                                           READY   STATUS    RESTARTS   AGE
kube-system   pod/calico-kube-controllers-558d465845-hfbwk   1/1     Running   0          4m45s
kube-system   pod/calico-node-5kvpg                          1/1     Running   0          3m54s
kube-system   pod/calico-node-c7bxh                          1/1     Running   0          3m54s
kube-system   pod/coredns-74cf88cc8f-7mg6p                   1/1     Running   0          4m37s
kube-system   pod/coredns-74cf88cc8f-88pwm                   1/1     Running   0          4m37s
kube-system   pod/konnectivity-agent-5b9589bd8-9xtbb         1/1     Running   0          4m36s
kube-system   pod/konnectivity-agent-5b9589bd8-gjl92         1/1     Running   0          4m36s
kube-system   pod/kube-proxy-zw5qv                           1/1     Running   0          3m54s
kube-system   pod/kube-proxy-zxpzd                           1/1     Running   0          3m54s
kube-system   pod/metrics-server-8499c9d7ff-kkdqn            1/1     Running   0          4m31s
```

### Install the nginx ingress controller

> Check the status until all the pods are in status `Running`!

See the official Exoscale documentation for more details [here](https://community.exoscale.com/documentation/sks/loadbalancer-ingress/#deploying-ingress-nginx-controller). The provided local file is modified to use Deployment as mentioned in the docs.

To install the nginx ingress controller, simply execute:

```bash
./set-all.sh ingress
```

The script waits until the NLB is provisioned and it's IP address is shown in the output:

```
job.batch/ingress-nginx-admission-patch created
ingressclass.networking.k8s.io/nginx created
networkpolicy.networking.k8s.io/ingress-nginx-admission created
validatingwebhookconfiguration.admissionregistration.k8s.io/ingress-nginx-admission created
Check the external IP of the LoadBalancer
LB has IP: 194.182.175.67
```

### Setup the host resolution

Change your local `/etc/hosts` file to add the necessary hosts to point to the public IP of the NLB:

```
194.182.175.67 app1.demo app2.demo
```

Check, if you can access the hosts by pinging them:

```bash
ping app1.demmo
ping app2.demo
```

- Deploy the application services

To deploy the demo services, execute:

```bash
./set-all.sh app
```

Check, if the services can be reached:

```bash
curl -v http://app1.demo/

curl -v http://app2.demo/
```

You should be able to check the applications also in your browser with the above URLs.

Check that the Server name starts with `app1` for http://app1.demo/ and `app2` for http://app2.demo/ respectively.

> the / is necessary at the end of the URLs at the moment!

- Clean up

To drop the whole SKS stack, simply execute:
```bash
./set-all.sh destroy
```
Check the status:

```bash
./set-all.sh
```
should return that it can't connect to the server.

**Note:** The NLB must be deleted manually from the console (why?) 