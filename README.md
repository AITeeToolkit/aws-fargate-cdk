# AWS Fargate CDK Deployment

This repository contains AWS CDK infrastructure code for deploying a containerized application on AWS Fargate.

## Features

- **Infrastructure as Code**: Complete AWS infrastructure defined using CDK
- **Container Orchestration**: ECS Fargate for serverless container deployment
- **CI/CD Pipeline**: Automated deployment using GitHub Actions and semantic-release
- **Parameter Management**: Secure parameter storage using AWS Systems Manager
- **Database**: PostgreSQL RDS instance with proper networking
- **Load Balancing**: Application Load Balancer for web traffic

## Architecture

The deployment includes:
- VPC with public/private subnets
- ECS Fargate services for API and Web applications
- RDS PostgreSQL database
- Application Load Balancer
- ECR repositories for container images
- Parameter Store for configuration management

## Deployment

The CI/CD pipeline automatically deploys on semantic releases. See `.github/workflows/` for workflow details.