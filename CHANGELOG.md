# Changelog

All notable changes to this project will be documented in this file. See [Conventional Commits](https://conventionalcommits.org) for commit guidelines.

## [1.5.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.4.0...v1.5.0) (2025-09-10)


### 🚀 Features

* add IAM stack with CI/CD user and CDK deployment permissions ([9d22c1d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9d22c1da8601fb2e26e328d20161bd9ddce37324))

## [1.4.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.3.0...v1.4.0) (2025-09-10)


### 🚀 Features

* update ECR repository paths to include environment and project name ([2d4ac50](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d4ac50479e264635a02822661addd9ddada287c))

## [1.3.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.2.0...v1.3.0) (2025-09-10)


### 🚀 Features

* add automatic deployment trigger after semantic release with version tracking ([d4fd2da](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d4fd2da829fed0f13c0a8b589f5544569c900a05))

## [1.2.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.1.1...v1.2.0) (2025-09-10)


### 🚀 Features

* add AWS credentials and ECR login steps to GitHub Actions workflow ([121b784](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/121b7845a6143c01f1ca5000e63bf285295b97d4))

## [1.1.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.1.0...v1.1.1) (2025-09-10)


### ♻️ Code Refactoring

* optimize CI workflow by extracting AWS login into separate reusable job ([c9b59c7](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c9b59c70c4e5607d251ebddd1dc5c52b8e841668))

## [1.1.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.0.1...v1.1.0) (2025-09-10)


### 🚀 Features

* replace ECR verification with automated CDK infrastructure deployment ([802a812](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/802a812c8ce9e06b3c6995a6232bd6604a4c9bfc))

## [1.0.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.0.0...v1.0.1) (2025-09-10)


### ♻️ Code Refactoring

* rename check-ecr-repos job to verify-setup and update token usage ([b2ae65f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b2ae65f2e55d567a61a933d18b527bc523a12b4d))

## 1.0.0 (2025-09-10)


### ♻️ Code Refactoring

* move AWS login to individual jobs and add ECR repo creation check ([b897ca9](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b897ca94755cecad33c101526b572ae65ca8db0a))
