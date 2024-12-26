A simple FastAPI app with scheduler setup to call the jira-process function every minute, it runs in the background which is independent of API endpoint calls
It checks JIRA issues's description and status, then proceed to create S3 bucket after the author validates and update the status to "Work in progress"
The app is deployed to AWS EKS with just a few simple components: deployment, built-in secret (not a best practice though), and ELB.


