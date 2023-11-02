$VILLAS_NAMESPACE="villas-deploy"

$CONFIG = (Get-Content -Raw ..\env_test.json | ConvertFrom-Json)

#this should really be stored somewhere else --> it is duplicated here.
$DB_USERNAME="xtopher"
$DB_PASSWORD="wolf0840"
$RDS_DB_INSTANCE_NAME = "villas-rds"
$DB_NAME = "villas"

$RDS_DB_INSTANCE_HOST = kubectl get dbinstance -n ${VILLAS_NAMESPACE} ${RDS_DB_INSTANCE_NAME} -o jsonpath='{.status.endpoint.address}'
$RDS_DB_INSTANCE_PORT = kubectl get dbinstance -n ${VILLAS_NAMESPACE} ${RDS_DB_INSTANCE_NAME} -o jsonpath='{.status.endpoint.port}'

Write-Output "postgresql://$($DB_USERNAME):$($DB_PASSWORD)@$($RDS_DB_INSTANCE_HOST):$($RDS_DB_INSTANCE_PORT)/$($DB_NAME)"
Write-Output " running on port $($RDS_DB_INSTANCE_PORT)"

Write-Output "    generate db_config_map.yaml" 
    (Get-Content .\db_config_map_template.yaml). 
        Replace('{VILLAS_NAMESPACE}', $VILLAS_NAMESPACE).
        Replace('{DB_USERNAME}', $DB_USERNAME).
        Replace('{DB_PASSWORD}', $DB_PASSWORD).
        Replace('{RDS_DB_INSTANCE_HOST}', $RDS_DB_INSTANCE_HOST).
        Replace('{RDS_DB_INSTANCE_PORT}', $RDS_DB_INSTANCE_PORT).
        Replace('{DB_NAME}', $DB_NAME).
        Replace('{AUTH0_BACKEND_CLIENT_ID}', $CONFIG.AUTH0_BACKEND_CLIENT_ID).
        Replace('{AUTH0_BACKEND_CLIENT_SECRET}', $CONFIG.AUTH0_BACKEND_CLIENT_SECRET).
        Replace('{AUTH0_MANAGEMENT_API_AUDIENCE}', $CONFIG.AUTH0_MANAGEMENT_API_AUDIENCE)|
        Set-Content .\db_config_map.yaml

Write-Output "Apply config map"
    kubectl apply -f db_config_map.yaml
    
Write-Output "Configure Villas service deployment"
    kubectl apply -f eks-villas-deployment.yaml
    kubectl apply -f eks-villas-service.yaml

Write-Output "Expose a load balancer in front of the cluster:"
    kubectl expose deployment -n ${VILLAS_NAMESPACE} eks-villas-linux-deployment --type=LoadBalancer --name=villas-external-service

    kubectl get deployments -n villas-deploy
    kubectl describe pods -n villas-deploy
    (kubectl describe services -n villas-deploy villas-external-service) -match 'LoadBalancer Ingress'

Write-Output "Monitor pods with kubectl get pods -n villas-deploy"
Write-Output "When the pods are running, complete the database set up with aws_villas_data_initialization.ps1"