Write-Output "Delete the database"
    kubectl delete dbinstance -n villas-deploy villas-rds

Write-Output "Delete the ACK pods"
    kubectl delete pods --all -n villas-ack-system

Write-Output "Delete the ACK security group"
    $RDS_SECURITY_GROUP_ID = Get-Content .\security-group.id
    aws ec2 delete-security-group --group-id=$RDS_SECURITY_GROUP_ID

Write-Output "Delete Villas deployment"
    kubectl delete deployment eks-villas-linux-deployment -n villas-deploy

Write-Output "Delete the cluster"

    eksctl delete cluster --region=us-east-2 --name=villas-cluster