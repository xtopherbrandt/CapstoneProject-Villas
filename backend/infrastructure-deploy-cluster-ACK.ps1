$env:AWS_AccESS_KEY_ID="AKIA5DCMERH7QVFU63RE"
$env:aws_secret_access_key="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"
$VILLAS_NAMESPACE="villas-deploy"
$VILLAS_ACK_NAMESPACE = "villas-ack-system"

Write-Output "Create cluster"
    eksctl create cluster --name villas-cluster --nodes=2 --version=1.27 --instance-types=t2.micro --region=us-east-2

Write-Output "Check nodes"
    kubectl get nodes

Write-Output "Create a Kubernetes namespace"
    kubectl create namespace $VILLAS_NAMESPACE

Write-Output "Cluster Identity Mapping"
    eksctl create iamidentitymapping --cluster villas-cluster --region=us-east-2 --arn arn:aws:iam::899955329535:user/Chris --group eks-console-dashboard-full-access-group --no-duplicate-arns
    eksctl create iamidentitymapping --cluster villas-cluster --region=us-east-2 --arn arn:aws:iam::899955329535:role/Kubernetes-Node-Viewer --group eks-console-dashboard-full-access-group --no-duplicate-arns

Write-Output "Create clusterrole and clusterrolebinding"
    kubectl apply -f https://s3.us-west-2.amazonaws.com/amazon-eks/docs/eks-console-full-access.yaml

Write-Output "Install ACK services controller"
    aws ecr-public get-login-password --region us-east-1 | helm registry login --username AWS --password-stdin public.ecr.aws
#        (note here: had to remove the "credsStore" key from the helm config.json before this would work)
    helm install --create-namespace -n villas-ack-system oci://public.ecr.aws/aws-controllers-k8s/rds-chart --version=0.0.27 --generate-name --set=aws.region=us-east-2
#        (note here: had to downgrade to helm 3.12.2 to avoid an authentication error with ECR)
    eksctl utils associate-iam-oidc-provider --cluster villas-cluster --region us-east-2 --approve

Write-Output "   update the ack-rds-controller role trust relationship with the oidc issuer uri"
    (aws eks describe-cluster --name villas-cluster --region us-east-2 --query "cluster.identity.oidc.issuer") -match '(?:"https://)(?<uri>.*)"'
    $OIDC_ISSUER_URI = $Matches.uri
    (Get-Content .\ack-rds-controller-role-trust-policy-template.json).Replace('{OIDC_ISSUER_URI}', $OIDC_ISSUER_URI) | Set-Content .\ack-rds-controller-role-trust-policy.json
    aws iam update-assume-role-policy --role-name ack-rds-controller --policy-document file://ack-rds-controller-role-trust-policy.json

Write-Output "Associate IAM ack-rds-role to service account"
#        (have the ack-rds-controller role hand crafted based on this article: https://aws-controllers-k8s.github.io/community/docs/user-docs/irsa/ )
    kubectl annotate serviceaccount -n $VILLAS_ACK_NAMESPACE ack-rds-controller eks.amazonaws.com/role-arn=arn:aws:iam::899955329535:role/ack-rds-controller
Write-Output "    Restart the pods:"
        $ACKDeployName = kubectl get deployments -n $VILLAS_ACK_NAMESPACE | Select-String -Pattern '(\S*)\d'
        kubectl -n $VILLAS_ACK_NAMESPACE rollout restart deployment $ACKDeployName.Matches.Value
        kubectl get pods -n $VILLAS_ACK_NAMESPACE

Write-Output "Set up database networking"
    $RDS_SUBNET_GROUP_NAME = "villas-subnets"
    $RDS_SUBNET_GROUP_DESCRIPTION = "subnets for the villas database"

Write-Output "    get the vpc:"
        $EKS_VPC_ID = aws eks describe-cluster --name villas-cluster --region us-east-2 --query "cluster.resourcesVpcConfig.vpcId" --output text
        Write-Output "      $($EKS_VPC_ID)"
        $EKS_VPC_Filter = "Name=vpc-id,Values=$($EKS_VPC_ID)"
Write-Output "    get the subnets:"
        $EKS_SUBNET_IDS = (aws ec2 describe-subnets --filters $EKS_VPC_Filter --query 'Subnets[*].SubnetId' --output text) -split "\s" 
        Write-Output "      $($EKS_SUBNET_IDS)"
        $EKS_SUBNET_IDS_YAML_FORMAT = foreach($s in $EKS_SUBNET_IDS){'- ',$s,"`n   " -join ""}

Write-Output "    generate db-subnet-groups.yaml" 
    (Get-Content .\db-subnet-groups-template.yaml). 
        Replace('{RDS_SUBNET_GROUP_DESCRIPTION}', $RDS_SUBNET_GROUP_DESCRIPTION).
        Replace('{VILLAS_NAMESPACE}', $VILLAS_NAMESPACE).
        Replace('{RDS_SUBNET_GROUP_NAME}', $RDS_SUBNET_GROUP_NAME).
        Replace('{SubnetList}', $EKS_SUBNET_IDS_YAML_FORMAT) |
        Set-Content .\db-subnet-groups.yaml
        
Write-Output "    create the subnet group:"
        kubectl apply -f db-subnet-groups.yaml

Write-Output "Set up Database Security group"
    $RDS_SECURITY_GROUP_NAME="villas-rds-security-group"
    $RDS_SECURITY_GROUP_DESCRIPTION="Authorizes the villas pods to access the database"
        
Write-Output "   get the CIDR block:"
    $EKS_CIDR_RANGE = aws ec2 describe-vpcs --vpc-ids $EKS_VPC_ID --query "Vpcs[].CidrBlock" --output text
Write-Output "    get the security group id:"
    $RDS_SECURITY_GROUP_ID = aws ec2 create-security-group --group-name "${RDS_SECURITY_GROUP_NAME}" --description "${RDS_SECURITY_GROUP_DESCRIPTION}" --vpc-id "${EKS_VPC_ID}" --output text
Write-Output "   store security group id in .\security-group.id"
    $RDS_SECURITY_GROUP_ID | Set-Content .\security-group.id
Write-Output "    authorize the pods to connect to the database on port 5432:"
    aws ec2 authorize-security-group-ingress --group-id "${RDS_SECURITY_GROUP_ID}" --protocol tcp --port 5432 --cidr "${EKS_CIDR_RANGE}"        

Write-Output "Set up PostgreSQL database instance"
Write-Output "    Create secret / master password:"
    $RDS_DB_USERNAME="xtopher"
    $RDS_DB_PASSWORD="wolf0840"
    $RDS_DB_INSTANCE_NAME = "villas-rds"
    $RDS_DB_NAME = "villas"

    kubectl create secret generic -n $VILLAS_NAMESPACE villas-rds-password --from-literal=username="${RDS_DB_USERNAME}" --from-literal=password="${RDS_DB_PASSWORD}"

Write-Output "    generate rds-postgres.yaml" 
    (Get-Content .\rds-postgres-template.yaml). 
        Replace('{RDS_DB_INSTANCE_NAME}', $RDS_DB_INSTANCE_NAME).
        Replace('{VILLAS_NAMESPACE}', $VILLAS_NAMESPACE).
        Replace('{RDS_SUBNET_GROUP_NAME}', $RDS_SUBNET_GROUP_NAME).
        Replace('{RDS_DB_USERNAME}', $RDS_DB_USERNAME).
        Replace('{RDS_SECURITY_GROUP_ID}', $RDS_SECURITY_GROUP_ID).
        Replace('{RDS_DB_NAME}', $RDS_DB_NAME) |
        Set-Content .\rds-postgres.yaml

Write-Output "    provision database:"
    #(note that the principle running these commands must have either the rds-service-role-creation policy or the manage-service-linked-roles policy
    #otherwise it results in an error: Unable to create the resource. Verify that you have permission to create service linked role.
    #see for more details:  http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAM.ServiceLinkedRoles.html)
    kubectl apply -f .\rds-postgres.yaml

    kubectl describe dbinstance -n "${APP_NAMESPACE}" "${RDS_DB_INSTANCE_NAME}"

Write-Output "    get the host and port of the deployed instance"
    $RDS_DB_INSTANCE_HOST = kubectl get dbinstance -n ${APP_NAMESPACE} ${RDS_DB_INSTANCE_NAME} -o jsonpath='{.status.endpoint.address}'
    $RDS_DB_INSTANCE_PORT = kubectl get dbinstance -n ${APP_NAMESPACE} ${RDS_DB_INSTANCE_NAME} -o jsonpath='{.status.endpoint.port}'

Write-Output "postgresql://$($RDS_DB_USERNAME):$($RDS_DB_PASSWORD)@$($RDS_DB_INSTANCE_HOST):$($RDS_DB_INSTANCE_PORT)/$($RDS_DB_NAME)"
Write-Output " running on port $($RDS_DB_INSTANCE_PORT)"
    
Write-Output "Set Environment Variables"
    kubectl set env pods --all USE_POD_ENV_CONFIG=True
    kubectl set env pods --all DB_USERNAME=$RDS_DB_USERNAME
    kubectl set env pods --all DB_PASSWORD=$RDS_DB_PASSWORD
    kubectl set env pods --all DB_NAME=$RDS_DB_NAME
    kubectl set env pods --all DB_HOST="$($RDS_DB_INSTANCE_HOST):$($RDS_DB_INSTANCE_PORT)"