# A simple FastAPI app with Jira integration and scheduler to create a S3 bucket

The issue is provided to the end user as a template with a fixed-format table and labeled "automated". 
End-users enter the required information, notifying the Platform team, who validates and updates the status to "Work in progress". 
Every minute, the app checks Jira issues, and if the status is updated to "Work in progress", it creates an S3 bucket.

## Deployment

The app is deployed to AWS Elastic Kubernetes Service (EKS) using the following components:

- **Deployment**: The app is packaged in a Kubernetes deployment.
- **Built-in Secret**: Secrets management is implemented (note: this is not considered a best practice).
- **Elastic Load Balancer (ELB)**: An ELB is used to expose the app.



