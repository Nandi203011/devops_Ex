# Exercise 10: Multi-Node Kubernetes Cluster with Multiple Applications and ReplicaSets

## Objective

Deploy two Flask microservices on a three-node Minikube cluster. Use
Kubernetes Deployments, automatically managed ReplicaSets, Services, and
pod anti-affinity to distribute replicas across nodes.

  Service           Application     Replicas
  ----------------- ------------- ----------
  Product Catalog   AppA                   2
  Shopping Cart     AppB                   3

## Environment

  Item                                              Value
  ------------------------------------------------- ---------------------------
  Operating system                                  Windows with PowerShell
  Kubernetes profile                                `devops-multinode`
  Kubernetes version shown by `kubectl get nodes`   `v1.37.0`
  Container platform                                Docker Desktop / Minikube
  Kubernetes namespace                              `default`

> **Note:** Minikube and Docker version numbers were not captured in the
> attached final screenshots, so they are not stated here.

## Applications and Docker images

The exercise uses two Flask applications:

-   `product_catalog.py` --- returns the product list at
    `GET /products`.
-   `shopping_cart.py` --- reads the cart at `GET /cart` and accepts an
    item at `POST /cart`.

The Docker images are built from these files:

-   `Dockerfile.product` → `product-catalog:latest`
-   `Dockerfile.shopping` → `shopping-cart:latest`

Build the images from the project directory:

``` powershell
docker build -t product-catalog:latest -f Dockerfile.product .
docker build -t shopping-cart:latest -f Dockerfile.shopping .
```

Load the local images into the Minikube profile:

``` powershell
minikube -p devops-multinode image load product-catalog:latest
minikube -p devops-multinode image load shopping-cart:latest
```

This workflow uses Minikube's image-loading feature; a registry add-on
is not required.

## Kubernetes manifests

The following manifests are used:

-   `product_catalog_deployment.yaml`
-   `shopping_cart_deployment.yaml`
-   `product_catalog_service.yaml`
-   `shopping_cart_service.yaml`

Both Deployments use `namespace: default`. Required pod anti-affinity
uses the topology key `kubernetes.io/hostname`, preventing replicas of
the same application from being scheduled on the same node.

Apply the manifests:

``` powershell
kubectl apply -f product_catalog_deployment.yaml
kubectl apply -f shopping_cart_deployment.yaml
kubectl apply -f product_catalog_service.yaml
kubectl apply -f shopping_cart_service.yaml
```

![Image load, docker images inside the node, and kubectl apply of all manifests (including the namespace error)]
(images/10_image_load_and_kubectl_apply.png)


## Verification: cluster and replica distribution

The final verification commands were:

``` powershell
kubectl get nodes
kubectl get deployments
kubectl get replicasets
kubectl get pods -o wide
kubectl get services
```

### Node status

All three nodes were `Ready`:

  Node                     Status   Role
  ------------------------ -------- ---------------
  `devops-multinode`       Ready    control-plane
  `devops-multinode-m02`   Ready    worker
  `devops-multinode-m03`   Ready    worker

### Deployment and ReplicaSet status

  Deployment            Desired   Ready   Available
  ------------------- --------- ------- -----------
  `product-catalog`           2       2           2
  `shopping-cart`             3       3           3

Both Deployments created their ReplicaSets successfully. The ReplicaSet
names shown in the final verification were `product-catalog-7cb85d4f`
and `shopping-cart-6858b5f797`.

### Pod-to-node distribution

The final `kubectl get pods -o wide` output showed five pods running
with `1/1` Ready and zero restarts:

  -----------------------------------------------------------------------------------
  Application pod                    Status                  Node
  ---------------------------------- ----------------------- ------------------------
  `product-catalog-7cb85d4f-j9prw`   Running, 1/1            `devops-multinode-m03`

  `product-catalog-7cb85d4f-vrzsp`   Running, 1/1            `devops-multinode-m02`

  `shopping-cart-6858b5f797-g47g8`   Running, 1/1            `devops-multinode`

  `shopping-cart-6858b5f797-lgt6p`   Running, 1/1            `devops-multinode-m03`

  `shopping-cart-6858b5f797-rlm2f`   Running, 1/1            `devops-multinode-m02`
  -----------------------------------------------------------------------------------

Therefore, Product Catalog has one replica on each of two different
nodes, and Shopping Cart has one replica on each of the three nodes.

![Final Kubernetes verification: three Ready nodes, deployments,
ReplicaSets, pod distribution, and
Services](images/10_kubernetes_cluster_verification.png)

## Services

The Services were created as `NodePort` Services in the `default`
namespace.

  Service                     Type       Cluster IP           NodePort
  --------------------------- ---------- ------------------ ----------
  `product-catalog-service`   NodePort   `10.96.235.201`       `32459`
  `shopping-cart-service`     NodePort   `10.107.231.141`      `32130`

For local access on Windows, start a Minikube service tunnel in a
PowerShell window and leave that window open:

``` powershell
minikube -p devops-multinode service product-catalog-service --url
minikube -p devops-multinode service shopping-cart-service --url
```

The local tunnel URLs and ports are temporary and may change when
restarted. Use the URLs printed by your own commands rather than
hard-coding a previous port.

## Application testing

### Test 1: Product Catalog

The following request succeeded:

``` powershell
curl.exe http://127.0.0.1:60170/products
```

The response contained the three configured products:

``` json
[
  {"id": 1, "name": "Laptop", "price": 1200},
  {"id": 2, "name": "Phone", "price": 800},
  {"id": 3, "name": "Headphones", "price": 150}
]
```

![Product Catalog endpoint returning the product
list](images/10_product_catalog_test.png)

### Test 2: Read the Shopping Cart

The cart endpoint responded to a GET request:

``` powershell
curl.exe http://127.0.0.1:60177/cart
```

An empty cart returns:

``` json
[]
```

### Test 3: Add an item to the Shopping Cart

A POST request was successfully sent using PowerShell's
`Invoke-RestMethod`:

``` powershell
$body = @{
    id = 1
    name = "Laptop"
    quantity = 1
} | ConvertTo-Json -Compress

Invoke-RestMethod -Uri "http://127.0.0.1:60177/cart" `
  -Method Post -ContentType "application/json" -Body $body
```
![Add an item to the Shopping Cart]
(images/10_curl_service_catalog.png)


The response contained the added Laptop item.

> **Important observation:** The cart is stored in an in-memory Python
> list inside each pod. The Service can route separate requests to
> different replicas, so one request may show the added item while
> another returns `[]`. This is expected for this sample implementation
> and does not indicate that the Deployment failed. A production
> application should use shared storage, such as Redis or a database,
> for consistent cart state.

## Summary

  Requirement                                   Result
  --------------------------------------------- ------------------------------------
  Three-node Minikube cluster                   Passed --- all three nodes `Ready`
  Product Catalog Deployment                    Passed --- 2/2 replicas ready
  Shopping Cart Deployment                      Passed --- 3/3 replicas ready
  ReplicaSets created by Deployments            Passed
  Replicas distributed across different nodes   Passed
  Product Catalog Service                       Passed
  Shopping Cart Service                         Passed
  `GET /products` returns product data          Passed
  `GET /cart` responds                          Passed
  `POST /cart` accepts an item                  Passed

**Conclusion:** The multi-node Kubernetes exercise is complete. Both
applications are deployed and accessible through Services, all five
replicas are healthy, and pod anti-affinity distributes replicas of each
application across separate nodes. The in-memory cart limitation is
documented above.
