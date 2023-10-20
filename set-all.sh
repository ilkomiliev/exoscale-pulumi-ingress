#!/usr/bin/env bash

set -eu -o pipefail

CLUSTER="cluster01"
ZONE="at-vie-1"
KUBE_CFG="$CLUSTER".kubecfg

deploy_ingress() {
  echo "Deploying the ingress controller"
  kubectl --kubeconfig "$KUBE_CFG" apply -f ingress-deploy.yaml

  echo "Check the external IP of the LoadBalancer"
  ip="$(kubectl --kubeconfig "$KUBE_CFG" get svc -n ingress-nginx |grep -i LoadBalancer | awk '{print $4}')"
  while [[ "$ip" == "<pending>" ]] ; do
      ip="$(kubectl --kubeconfig "$KUBE_CFG" get svc -n ingress-nginx |grep -i LoadBalancer | awk '{print $4}')"
      sleep 1
  done

  echo "LB has IP: $ip"
}

deploy_sks() {
  echo "Activating the python virt env"
  source ./venv/bin/activate

  echo "Running pulumi stack"
  pulumi up -y

  echo "Obtaining kubeconfig"
  exo compute sks kubeconfig "$CLUSTER" kube-admin --zone "$ZONE" --group system:masters > "$KUBE_CFG"
}

destroy_sks() {
  echo "Destroying SKS"
  pulumi destroy
}

deploy_services() {
  echo "Deploying app services"
  kubectl --kubeconfig "$KUBE_CFG" apply -f service-ingress.yaml
}

status() {
  echo "List all kubernetes resources"
  kubectl --kubeconfig "$KUBE_CFG" get all --all-namespaces
}

case "${1:-status}" in
    sks)
        deploy_sks
        ;;

    ingress)
        deploy_ingress
        ;;

    app)
        deploy_services
        ;;

    status)
        status
        ;;

    destroy)
      destroy_sks
      ;;

    *)
        echo "Unknown option use one of sks|ingress|app|status (default)"
esac