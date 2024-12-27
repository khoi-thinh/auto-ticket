# A simple FastAPI app that integrates with Jira and uses a scheduler to create an S3 bucket based on Jira ticket updates

- A fixed-format table is provided to end-users and labeled "automated".  
- End-users fill in the required information and notifies the Platform team, the team validates the information and updates the ticket status to "Work in progress".  
- Every minute, the app checks Jira issues, if the status is updated to "Work in progress", the app creates an S3 bucket and adds a comment to the ticket.

An example of template's table format    
![image](https://github.com/user-attachments/assets/e343afb6-1ea9-4bbf-a1d7-cc6aaefbc188)


## Deployment

The app is deployed to AWS Elastic Kubernetes Service (EKS) using the following components:

- **Deployment**: The app is packaged in a Kubernetes deployment.
- **Built-in Secret**: Secrets management is implemented to avoid pushing secret.yaml to GitHub, the JIRA token is securely stored in AWS Secrets Manager (us-east-1), and a script that retrieves the secret from AWS Secrets Manager and creates a secret is included in the GitHub Actions flow.
- **Elastic Load Balancer (ELB)**: An ELB is used to expose the app.
- **AWS Secrets Manager**: AWS access keys, secrets (for each project) are securely stored in AWS Secrets Manager in us-east-1.

## Note
- EKS should have permission in its attached role to retrieve the secret value (secretsmanager:GetSecretValue action)



