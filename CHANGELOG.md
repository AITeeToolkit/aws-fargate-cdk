# Changelog

All notable changes to this project will be documented in this file. See [Conventional Commits](https://conventionalcommits.org) for commit guidelines.

## [1.16.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.15.0...v1.16.0) (2025-09-15)


### 🚀 Features

* add deployment and database migration scripts with AWS SSO support ([9280305](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/92803058aa4b4c9d143c74fddf3de7e06b7d91fa))
* add dynamic image tag support for API and web service deployments ([9e08016](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9e08016e708ba95b100ecc9bb45eb5b7118e2b08))
* add latest tag and SSM VPC endpoint for ECS secrets management ([b8f764b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b8f764b75a934c57d8b24f1d015121641e6655cc))
* add security group with VPC ingress rules for RDS PostgreSQL instance ([5f820c1](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5f820c1b3bfd99b0b93d86e6d466e17b2cb62e2b))
* add service discovery and parameter store configuration for API and database stacks ([7059def](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7059defeb0744eac607374b3f9f438bb24c878c7))
* enable public access by default in database stack configuration ([6ee6962](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6ee6962eecd36fa58587a97abed30c9f094af3ce))
* refactor ALB architecture to support multiple domains with separate load balancers ([88c4c25](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/88c4c254b58a7a01688ae7261ad5718c70acac2a))
* store database connection details in SSM Parameter Store to remove CloudFormation dependencies ([7d6e7fa](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7d6e7fa6e7257c65d34d2575fc0fbec49529650e))


### 🐛 Bug Fixes

* delete existing git tags before running semantic-release to prevent conflicts ([cae3b7c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/cae3b7ca2322f3d52ec80cc473aa02c1a3f340ca))
* improve tag cleanup by removing orphaned local tags before semantic release ([43c8332](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/43c833219a094cf83cddad4ec37fb82aaecbdb09))
* only delete semantic-release tag if it conflicts with next version ([52e0276](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/52e027665f73e1f26651b9a121f05445dc44006c))
* simplify tag cleanup logic in semantic-release workflow ([608885f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/608885fb0f5d1267db94b1cc3102d5e7622b2add))
* update health check configuration with standard path and intervals ([e63a6a3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e63a6a31c5fbb071d1d3601dcccef2800409f8b7))
* update RDS username from dbadmin to postgres for consistency ([6793ef8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6793ef8a0967fedacd00f61cbb2a2f796a33ac4e))


### ♻️ Code Refactoring

* add feature branch support and configurable public/private DB subnet selection ([d72a2ec](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d72a2ec2ed0956ac2ad0cd2cd2525c19f0817eab))
* add toggle switch for selecting public/private subnet group in database stack ([8fadb55](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8fadb55f5277af8b99a130904dc1110e41f15d5a))
* migrate VPC to fully isolated private subnets with VPC endpoints ([ce750cf](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ce750cff2bbbf48e4881683b07cfd846b078e4f6))
* optimize VPC endpoint security groups and consolidate IAM permissions for ECS tasks ([132bbcc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/132bbcc847d9f6472fdd19af3324dda68bdccb82))
* refactored infra deployment to cdk; completed domain automation; storefront operational ([9456c93](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9456c93798856f15f00971fb89e05259c56aa2d9))
* remove unused parameters stack and imports ([4328e0a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4328e0a41a53c132f0021a45e15926bdfe4425e8))
* remove unused ParametersStack from CDK app deployment ([fecbeb0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/fecbeb04f12c3f95b4b0a9b7faedd0d92db61ed9))
* reorder stack deployment to enable IAM and move parameters after database ([df3f9ee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/df3f9ee17aa560f4cc08ec33dc077f17f88d02b7))
* simplify RDS subnet configuration to use mixed subnet group with public/private toggle ([d2139ff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d2139ff630c2f7fe63a3576b5d5031615da4421f))
* split image tag generation into separate reusable workflow job ([6ce1b88](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6ce1b889e74fa91a24342756afa641e47b43a291))
* use database secrets directly in API service and simplify ECR repository setup ([2fdf9e0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2fdf9e092747d680e95941edfce53de26a5d371c))

## [1.16.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.15.0...v1.16.0) (2025-09-15)


### 🚀 Features

* add deployment and database migration scripts with AWS SSO support ([9280305](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/92803058aa4b4c9d143c74fddf3de7e06b7d91fa))
* add dynamic image tag support for API and web service deployments ([9e08016](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9e08016e708ba95b100ecc9bb45eb5b7118e2b08))
* add latest tag and SSM VPC endpoint for ECS secrets management ([b8f764b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b8f764b75a934c57d8b24f1d015121641e6655cc))
* add security group with VPC ingress rules for RDS PostgreSQL instance ([5f820c1](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5f820c1b3bfd99b0b93d86e6d466e17b2cb62e2b))
* add service discovery and parameter store configuration for API and database stacks ([7059def](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7059defeb0744eac607374b3f9f438bb24c878c7))
* enable public access by default in database stack configuration ([6ee6962](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6ee6962eecd36fa58587a97abed30c9f094af3ce))
* refactor ALB architecture to support multiple domains with separate load balancers ([88c4c25](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/88c4c254b58a7a01688ae7261ad5718c70acac2a))
* store database connection details in SSM Parameter Store to remove CloudFormation dependencies ([7d6e7fa](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7d6e7fa6e7257c65d34d2575fc0fbec49529650e))


### 🐛 Bug Fixes

* delete existing git tags before running semantic-release to prevent conflicts ([cae3b7c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/cae3b7ca2322f3d52ec80cc473aa02c1a3f340ca))
* improve tag cleanup by removing orphaned local tags before semantic release ([43c8332](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/43c833219a094cf83cddad4ec37fb82aaecbdb09))
* only delete semantic-release tag if it conflicts with next version ([52e0276](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/52e027665f73e1f26651b9a121f05445dc44006c))
* simplify tag cleanup logic in semantic-release workflow ([608885f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/608885fb0f5d1267db94b1cc3102d5e7622b2add))
* update health check configuration with standard path and intervals ([e63a6a3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e63a6a31c5fbb071d1d3601dcccef2800409f8b7))
* update RDS username from dbadmin to postgres for consistency ([6793ef8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6793ef8a0967fedacd00f61cbb2a2f796a33ac4e))


### ♻️ Code Refactoring

* add feature branch support and configurable public/private DB subnet selection ([d72a2ec](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d72a2ec2ed0956ac2ad0cd2cd2525c19f0817eab))
* add toggle switch for selecting public/private subnet group in database stack ([8fadb55](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8fadb55f5277af8b99a130904dc1110e41f15d5a))
* migrate VPC to fully isolated private subnets with VPC endpoints ([ce750cf](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ce750cff2bbbf48e4881683b07cfd846b078e4f6))
* optimize VPC endpoint security groups and consolidate IAM permissions for ECS tasks ([132bbcc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/132bbcc847d9f6472fdd19af3324dda68bdccb82))
* refactored infra deployment to cdk; completed domain automation; storefront operational ([9456c93](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9456c93798856f15f00971fb89e05259c56aa2d9))
* remove unused parameters stack and imports ([4328e0a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4328e0a41a53c132f0021a45e15926bdfe4425e8))
* remove unused ParametersStack from CDK app deployment ([fecbeb0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/fecbeb04f12c3f95b4b0a9b7faedd0d92db61ed9))
* reorder stack deployment to enable IAM and move parameters after database ([df3f9ee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/df3f9ee17aa560f4cc08ec33dc077f17f88d02b7))
* simplify RDS subnet configuration to use mixed subnet group with public/private toggle ([d2139ff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d2139ff630c2f7fe63a3576b5d5031615da4421f))
* split image tag generation into separate reusable workflow job ([6ce1b88](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6ce1b889e74fa91a24342756afa641e47b43a291))
* use database secrets directly in API service and simplify ECR repository setup ([2fdf9e0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2fdf9e092747d680e95941edfce53de26a5d371c))

## [1.16.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.15.0...v1.16.0) (2025-09-15)


### 🚀 Features

* add deployment and database migration scripts with AWS SSO support ([9280305](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/92803058aa4b4c9d143c74fddf3de7e06b7d91fa))
* add dynamic image tag support for API and web service deployments ([9e08016](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9e08016e708ba95b100ecc9bb45eb5b7118e2b08))
* add latest tag and SSM VPC endpoint for ECS secrets management ([b8f764b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b8f764b75a934c57d8b24f1d015121641e6655cc))
* add security group with VPC ingress rules for RDS PostgreSQL instance ([5f820c1](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5f820c1b3bfd99b0b93d86e6d466e17b2cb62e2b))
* add service discovery and parameter store configuration for API and database stacks ([7059def](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7059defeb0744eac607374b3f9f438bb24c878c7))
* enable public access by default in database stack configuration ([6ee6962](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6ee6962eecd36fa58587a97abed30c9f094af3ce))
* refactor ALB architecture to support multiple domains with separate load balancers ([88c4c25](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/88c4c254b58a7a01688ae7261ad5718c70acac2a))
* store database connection details in SSM Parameter Store to remove CloudFormation dependencies ([7d6e7fa](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7d6e7fa6e7257c65d34d2575fc0fbec49529650e))


### 🐛 Bug Fixes

* delete existing git tags before running semantic-release to prevent conflicts ([cae3b7c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/cae3b7ca2322f3d52ec80cc473aa02c1a3f340ca))
* improve tag cleanup by removing orphaned local tags before semantic release ([43c8332](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/43c833219a094cf83cddad4ec37fb82aaecbdb09))
* only delete semantic-release tag if it conflicts with next version ([52e0276](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/52e027665f73e1f26651b9a121f05445dc44006c))
* update health check configuration with standard path and intervals ([e63a6a3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e63a6a31c5fbb071d1d3601dcccef2800409f8b7))
* update RDS username from dbadmin to postgres for consistency ([6793ef8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6793ef8a0967fedacd00f61cbb2a2f796a33ac4e))


### ♻️ Code Refactoring

* add feature branch support and configurable public/private DB subnet selection ([d72a2ec](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d72a2ec2ed0956ac2ad0cd2cd2525c19f0817eab))
* add toggle switch for selecting public/private subnet group in database stack ([8fadb55](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8fadb55f5277af8b99a130904dc1110e41f15d5a))
* migrate VPC to fully isolated private subnets with VPC endpoints ([ce750cf](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ce750cff2bbbf48e4881683b07cfd846b078e4f6))
* optimize VPC endpoint security groups and consolidate IAM permissions for ECS tasks ([132bbcc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/132bbcc847d9f6472fdd19af3324dda68bdccb82))
* refactored infra deployment to cdk; completed domain automation; storefront operational ([9456c93](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9456c93798856f15f00971fb89e05259c56aa2d9))
* remove unused parameters stack and imports ([4328e0a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4328e0a41a53c132f0021a45e15926bdfe4425e8))
* remove unused ParametersStack from CDK app deployment ([fecbeb0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/fecbeb04f12c3f95b4b0a9b7faedd0d92db61ed9))
* reorder stack deployment to enable IAM and move parameters after database ([df3f9ee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/df3f9ee17aa560f4cc08ec33dc077f17f88d02b7))
* simplify RDS subnet configuration to use mixed subnet group with public/private toggle ([d2139ff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d2139ff630c2f7fe63a3576b5d5031615da4421f))
* split image tag generation into separate reusable workflow job ([6ce1b88](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6ce1b889e74fa91a24342756afa641e47b43a291))
* use database secrets directly in API service and simplify ECR repository setup ([2fdf9e0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2fdf9e092747d680e95941edfce53de26a5d371c))

## [1.16.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.15.1...v1.16.0) (2025-09-15)


### 🚀 Features

* add deployment and database migration scripts with AWS SSO support ([9280305](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/92803058aa4b4c9d143c74fddf3de7e06b7d91fa))
* add dynamic image tag support for API and web service deployments ([9e08016](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9e08016e708ba95b100ecc9bb45eb5b7118e2b08))
* add latest tag and SSM VPC endpoint for ECS secrets management ([b8f764b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b8f764b75a934c57d8b24f1d015121641e6655cc))
* add security group with VPC ingress rules for RDS PostgreSQL instance ([5f820c1](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5f820c1b3bfd99b0b93d86e6d466e17b2cb62e2b))
* add service discovery and parameter store configuration for API and database stacks ([7059def](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7059defeb0744eac607374b3f9f438bb24c878c7))
* enable public access by default in database stack configuration ([6ee6962](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6ee6962eecd36fa58587a97abed30c9f094af3ce))
* refactor ALB architecture to support multiple domains with separate load balancers ([88c4c25](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/88c4c254b58a7a01688ae7261ad5718c70acac2a))
* store database connection details in SSM Parameter Store to remove CloudFormation dependencies ([7d6e7fa](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7d6e7fa6e7257c65d34d2575fc0fbec49529650e))


### 🐛 Bug Fixes

* delete existing git tags before running semantic-release to prevent conflicts ([cae3b7c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/cae3b7ca2322f3d52ec80cc473aa02c1a3f340ca))
* improve tag cleanup by removing orphaned local tags before semantic release ([43c8332](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/43c833219a094cf83cddad4ec37fb82aaecbdb09))
* update health check configuration with standard path and intervals ([e63a6a3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e63a6a31c5fbb071d1d3601dcccef2800409f8b7))
* update RDS username from dbadmin to postgres for consistency ([6793ef8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6793ef8a0967fedacd00f61cbb2a2f796a33ac4e))


### ♻️ Code Refactoring

* add toggle switch for selecting public/private subnet group in database stack ([8fadb55](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8fadb55f5277af8b99a130904dc1110e41f15d5a))
* migrate VPC to fully isolated private subnets with VPC endpoints ([ce750cf](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ce750cff2bbbf48e4881683b07cfd846b078e4f6))
* optimize VPC endpoint security groups and consolidate IAM permissions for ECS tasks ([132bbcc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/132bbcc847d9f6472fdd19af3324dda68bdccb82))
* refactored infra deployment to cdk; completed domain automation; storefront operational ([9456c93](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9456c93798856f15f00971fb89e05259c56aa2d9))
* remove unused parameters stack and imports ([4328e0a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4328e0a41a53c132f0021a45e15926bdfe4425e8))
* remove unused ParametersStack from CDK app deployment ([fecbeb0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/fecbeb04f12c3f95b4b0a9b7faedd0d92db61ed9))
* reorder stack deployment to enable IAM and move parameters after database ([df3f9ee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/df3f9ee17aa560f4cc08ec33dc077f17f88d02b7))
* simplify RDS subnet configuration to use mixed subnet group with public/private toggle ([d2139ff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d2139ff630c2f7fe63a3576b5d5031615da4421f))
* use database secrets directly in API service and simplify ECR repository setup ([2fdf9e0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2fdf9e092747d680e95941edfce53de26a5d371c))

## [1.16.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.15.1...v1.16.0) (2025-09-15)


### 🚀 Features

* add deployment and database migration scripts with AWS SSO support ([9280305](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/92803058aa4b4c9d143c74fddf3de7e06b7d91fa))
* add dynamic image tag support for API and web service deployments ([9e08016](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9e08016e708ba95b100ecc9bb45eb5b7118e2b08))
* add latest tag and SSM VPC endpoint for ECS secrets management ([b8f764b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b8f764b75a934c57d8b24f1d015121641e6655cc))
* add security group with VPC ingress rules for RDS PostgreSQL instance ([5f820c1](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5f820c1b3bfd99b0b93d86e6d466e17b2cb62e2b))
* add service discovery and parameter store configuration for API and database stacks ([7059def](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7059defeb0744eac607374b3f9f438bb24c878c7))
* enable public access by default in database stack configuration ([6ee6962](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6ee6962eecd36fa58587a97abed30c9f094af3ce))
* refactor ALB architecture to support multiple domains with separate load balancers ([88c4c25](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/88c4c254b58a7a01688ae7261ad5718c70acac2a))
* store database connection details in SSM Parameter Store to remove CloudFormation dependencies ([7d6e7fa](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7d6e7fa6e7257c65d34d2575fc0fbec49529650e))


### 🐛 Bug Fixes

* delete existing git tags before running semantic-release to prevent conflicts ([cae3b7c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/cae3b7ca2322f3d52ec80cc473aa02c1a3f340ca))
* update health check configuration with standard path and intervals ([e63a6a3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e63a6a31c5fbb071d1d3601dcccef2800409f8b7))
* update RDS username from dbadmin to postgres for consistency ([6793ef8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6793ef8a0967fedacd00f61cbb2a2f796a33ac4e))


### ♻️ Code Refactoring

* add toggle switch for selecting public/private subnet group in database stack ([8fadb55](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8fadb55f5277af8b99a130904dc1110e41f15d5a))
* migrate VPC to fully isolated private subnets with VPC endpoints ([ce750cf](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ce750cff2bbbf48e4881683b07cfd846b078e4f6))
* optimize VPC endpoint security groups and consolidate IAM permissions for ECS tasks ([132bbcc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/132bbcc847d9f6472fdd19af3324dda68bdccb82))
* refactored infra deployment to cdk; completed domain automation; storefront operational ([9456c93](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9456c93798856f15f00971fb89e05259c56aa2d9))
* remove unused parameters stack and imports ([4328e0a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4328e0a41a53c132f0021a45e15926bdfe4425e8))
* remove unused ParametersStack from CDK app deployment ([fecbeb0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/fecbeb04f12c3f95b4b0a9b7faedd0d92db61ed9))
* reorder stack deployment to enable IAM and move parameters after database ([df3f9ee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/df3f9ee17aa560f4cc08ec33dc077f17f88d02b7))
* simplify RDS subnet configuration to use mixed subnet group with public/private toggle ([d2139ff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d2139ff630c2f7fe63a3576b5d5031615da4421f))
* use database secrets directly in API service and simplify ECR repository setup ([2fdf9e0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2fdf9e092747d680e95941edfce53de26a5d371c))

## [1.16.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.15.1...v1.16.0) (2025-09-15)


### 🚀 Features

* add deployment and database migration scripts with AWS SSO support ([9280305](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/92803058aa4b4c9d143c74fddf3de7e06b7d91fa))
* add dynamic image tag support for API and web service deployments ([9e08016](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9e08016e708ba95b100ecc9bb45eb5b7118e2b08))
* add latest tag and SSM VPC endpoint for ECS secrets management ([b8f764b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b8f764b75a934c57d8b24f1d015121641e6655cc))
* add security group with VPC ingress rules for RDS PostgreSQL instance ([5f820c1](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5f820c1b3bfd99b0b93d86e6d466e17b2cb62e2b))
* add service discovery and parameter store configuration for API and database stacks ([7059def](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7059defeb0744eac607374b3f9f438bb24c878c7))
* enable public access by default in database stack configuration ([6ee6962](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6ee6962eecd36fa58587a97abed30c9f094af3ce))
* refactor ALB architecture to support multiple domains with separate load balancers ([88c4c25](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/88c4c254b58a7a01688ae7261ad5718c70acac2a))
* store database connection details in SSM Parameter Store to remove CloudFormation dependencies ([7d6e7fa](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7d6e7fa6e7257c65d34d2575fc0fbec49529650e))


### 🐛 Bug Fixes

* update health check configuration with standard path and intervals ([e63a6a3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e63a6a31c5fbb071d1d3601dcccef2800409f8b7))
* update RDS username from dbadmin to postgres for consistency ([6793ef8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6793ef8a0967fedacd00f61cbb2a2f796a33ac4e))


### ♻️ Code Refactoring

* add toggle switch for selecting public/private subnet group in database stack ([8fadb55](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8fadb55f5277af8b99a130904dc1110e41f15d5a))
* migrate VPC to fully isolated private subnets with VPC endpoints ([ce750cf](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ce750cff2bbbf48e4881683b07cfd846b078e4f6))
* optimize VPC endpoint security groups and consolidate IAM permissions for ECS tasks ([132bbcc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/132bbcc847d9f6472fdd19af3324dda68bdccb82))
* refactored infra deployment to cdk; completed domain automation; storefront operational ([9456c93](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9456c93798856f15f00971fb89e05259c56aa2d9))
* remove unused parameters stack and imports ([4328e0a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4328e0a41a53c132f0021a45e15926bdfe4425e8))
* remove unused ParametersStack from CDK app deployment ([fecbeb0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/fecbeb04f12c3f95b4b0a9b7faedd0d92db61ed9))
* reorder stack deployment to enable IAM and move parameters after database ([df3f9ee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/df3f9ee17aa560f4cc08ec33dc077f17f88d02b7))
* simplify RDS subnet configuration to use mixed subnet group with public/private toggle ([d2139ff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d2139ff630c2f7fe63a3576b5d5031615da4421f))
* use database secrets directly in API service and simplify ECR repository setup ([2fdf9e0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2fdf9e092747d680e95941edfce53de26a5d371c))

## [1.16.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.15.1...v1.16.0) (2025-09-15)


### 🚀 Features

* add deployment and database migration scripts with AWS SSO support ([9280305](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/92803058aa4b4c9d143c74fddf3de7e06b7d91fa))
* add dynamic image tag support for API and web service deployments ([9e08016](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9e08016e708ba95b100ecc9bb45eb5b7118e2b08))
* add latest tag and SSM VPC endpoint for ECS secrets management ([b8f764b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b8f764b75a934c57d8b24f1d015121641e6655cc))
* add security group with VPC ingress rules for RDS PostgreSQL instance ([5f820c1](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5f820c1b3bfd99b0b93d86e6d466e17b2cb62e2b))
* add service discovery and parameter store configuration for API and database stacks ([7059def](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7059defeb0744eac607374b3f9f438bb24c878c7))
* enable public access by default in database stack configuration ([6ee6962](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6ee6962eecd36fa58587a97abed30c9f094af3ce))
* refactor ALB architecture to support multiple domains with separate load balancers ([88c4c25](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/88c4c254b58a7a01688ae7261ad5718c70acac2a))
* store database connection details in SSM Parameter Store to remove CloudFormation dependencies ([7d6e7fa](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7d6e7fa6e7257c65d34d2575fc0fbec49529650e))


### 🐛 Bug Fixes

* update RDS username from dbadmin to postgres for consistency ([6793ef8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6793ef8a0967fedacd00f61cbb2a2f796a33ac4e))


### ♻️ Code Refactoring

* add toggle switch for selecting public/private subnet group in database stack ([8fadb55](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8fadb55f5277af8b99a130904dc1110e41f15d5a))
* migrate VPC to fully isolated private subnets with VPC endpoints ([ce750cf](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ce750cff2bbbf48e4881683b07cfd846b078e4f6))
* optimize VPC endpoint security groups and consolidate IAM permissions for ECS tasks ([132bbcc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/132bbcc847d9f6472fdd19af3324dda68bdccb82))
* refactored infra deployment to cdk; completed domain automation; storefront operational ([9456c93](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9456c93798856f15f00971fb89e05259c56aa2d9))
* remove unused parameters stack and imports ([4328e0a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4328e0a41a53c132f0021a45e15926bdfe4425e8))
* remove unused ParametersStack from CDK app deployment ([fecbeb0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/fecbeb04f12c3f95b4b0a9b7faedd0d92db61ed9))
* reorder stack deployment to enable IAM and move parameters after database ([df3f9ee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/df3f9ee17aa560f4cc08ec33dc077f17f88d02b7))
* simplify RDS subnet configuration to use mixed subnet group with public/private toggle ([d2139ff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d2139ff630c2f7fe63a3576b5d5031615da4421f))
* use database secrets directly in API service and simplify ECR repository setup ([2fdf9e0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2fdf9e092747d680e95941edfce53de26a5d371c))

## [1.15.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.15.0...v1.15.1) (2025-09-11)


### ♻️ Code Refactoring

* add feature branch support and configurable public/private DB subnet selection ([d72a2ec](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d72a2ec2ed0956ac2ad0cd2cd2525c19f0817eab))
* split image tag generation into separate reusable workflow job ([6ce1b88](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6ce1b889e74fa91a24342756afa641e47b43a291))

## [1.15.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.14.1...v1.15.0) (2025-09-11)


### 🚀 Features

* add configurable subnet group selection for RDS instance deployment ([057c7f9](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/057c7f997f8522ed85f1c9c44cdeefa146b2aa02))

## [1.14.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.14.0...v1.14.1) (2025-09-11)


### ♻️ Code Refactoring

* simplify RDS subnet configuration by removing subnet group abstraction ([07bd591](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/07bd591145dea7e49c9c02e50a0083bb8519d3a5))

## [1.14.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.13.0...v1.14.0) (2025-09-11)


### 🚀 Features

* add configurable public/private subnet support for RDS database instance ([650ac1a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/650ac1a1cf0f6396e7ae9f863f40478fc3bcf795))

## [1.13.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.12.0...v1.13.0) (2025-09-11)


### 🚀 Features

* add production deployment and detailed deployment summary to release workflow ([bb278b1](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bb278b1b28fdeef4ee5a4e59c181d462d7126ffd))

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
