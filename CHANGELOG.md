# Changelog

All notable changes to this project will be documented in this file. See [Conventional Commits](https://conventionalcommits.org) for commit guidelines.

## [1.12.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.11.4...v1.12.0) (2025-09-11)


### 🚀 Features

* enable public access to RDS database instance in public subnet ([082d91d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/082d91d10738ae66e7689d7433a768e712fa7349))

## [1.11.4](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.11.3...v1.11.4) (2025-09-11)


### 🐛 Bug Fixes

* create execution role explicitly to avoid NoneType error ([510fa04](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/510fa045c876f21c0878c8485ddf8fbe65f0b452))

## [1.11.3](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.11.2...v1.11.3) (2025-09-11)


### 🐛 Bug Fixes

* add comprehensive IAM permissions for ECS Fargate services ([7c9b639](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7c9b639540bdbb9015e6fd7bb714653443010ac9))

## [1.11.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.11.1...v1.11.2) (2025-09-11)


### 🐛 Bug Fixes

* downgrade PostgreSQL database version from 16.2 to 15.2 ([5a23bf0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5a23bf02269da4a648c643adde3cd6799ec0125a))

## [1.11.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.11.0...v1.11.1) (2025-09-11)


### ♻️ Code Refactoring

* remove unused ParametersStack import from app.py ([19d5adf](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/19d5adf5dcca1e4a0e3ef5f032a73db00f47ce34))

## [1.11.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.10.0...v1.11.0) (2025-09-11)


### 🚀 Features

* add ECR and SSM parameter store permissions to Fargate task role ([4f0830f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4f0830ff2d5dde5abc4e87e8f9fc436c290565c5))

## [1.10.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.9.0...v1.10.0) (2025-09-11)


### 🚀 Features

* add comprehensive README documentation ([8c58cbd](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8c58cbd0613b238d6cdae13ad8e61d274d68fdea))

## [1.9.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.8.2...v1.9.0) (2025-09-11)


### 🚀 Features

* make ALB listener configuration optional for private Fargate services ([d12690d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d12690d36afbb2ac03c29ecbe01564e7059c0f8a))

## [1.8.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.8.1...v1.8.2) (2025-09-11)


### 🐛 Bug Fixes

* downgrade Postgres version from 15.8 to 15.2 in database stack ([72ecf7e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72ecf7e1e62a3662d6d58f0d37ce938b1c9dc85f))

## [1.8.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.8.0...v1.8.1) (2025-09-11)


### ♻️ Code Refactoring

* update workflow inputs structure and add post-deployment notification ([20d5101](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/20d510154ac7823c1d91e4187704682a6afd2178))

## [1.8.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.7.1...v1.8.0) (2025-09-11)


### 🚀 Features

* add API service stack and integrate secrets management for web/API services ([3ecb368](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3ecb3680290acba3bd4bfbd542dbe8ddd074fe37))

## [1.7.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.7.0...v1.7.1) (2025-09-10)


### 🐛 Bug Fixes

* remove unnecessary dependency between network and IAM stacks ([369fc86](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/369fc86d7812bc8e480563bbe0a3bf1b6dd3f46c))

## [1.7.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.6.0...v1.7.0) (2025-09-10)


### 🚀 Features

* expand IAM permissions to support CDK bootstrap and deployment ([3e8ebfa](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3e8ebfaab8ccbe53b792bcbcf25c946f955ea9b1))

## [1.6.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.5.0...v1.6.0) (2025-09-10)


### 🚀 Features

* add CDK bootstrap step before deployment in GitHub Actions workflow ([f0aabd8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f0aabd8f6c60dba6a1bf0b363d1729c048c2b601))
* add dependency between IAM and network stacks to enforce deployment order ([85391bc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/85391bc634270f38acf8679370b56056937d741c))

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
