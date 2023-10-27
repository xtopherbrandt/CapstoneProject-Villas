Write-Output "Get a pod name"
    $POD_NAME_MATCH = (kubectl get pods -n villas-deploy) | Select-Object -First 1 -Skip 1 | Select-String -Pattern '(?<name>\S*)'
    $POD_NAME = $POD_NAME_MATCH.matches.value
    Write-Output "$(${POD_NAME})"

Write-Output "Initialize the Database with Flask db Upgrade "
    kubectl exec -it -n villas-deploy ${POD_NAME} -- flask db upgrade

Write-Output "Import Province and Country Table data"
    kubectl exec -it -n villas-deploy ${POD_NAME} -- python insert_enum_data_in_db.py
