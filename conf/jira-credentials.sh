#!/bin/bash

SECRET_NAME="jira"
REGION="us-east-1"

# Retrieve secret from Secrets Manager
SECRET_VALUE=$(aws secretsmanager get-secret-value --secret-id $SECRET_NAME --region $REGION --query 'SecretString' --output text)

# Parse the JSON secret
JIRA_SERVER=$(echo "$SECRET_VALUE" | jq -r .JIRA_SERVER)
JIRA_USERNAME=$(echo "$SECRET_VALUE" | jq -r .JIRA_USERNAME)
JIRA_API_TOKEN=$(echo "$SECRET_VALUE" | jq -r .JIRA_API_TOKEN)

# Create Kubernetes Secret
kubectl create secret generic jira-credentials \
  --from-literal=JIRA_SERVER="$JIRA_SERVER" \
  --from-literal=JIRA_USERNAME="$JIRA_USERNAME" \
  --from-literal=JIRA_API_TOKEN="$JIRA_API_TOKEN" \
  --dry-run=client -o yaml | kubectl apply -f -
