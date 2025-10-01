# Changelog

All notable changes to this project will be documented in this file. See [Conventional Commits](https://conventionalcommits.org) for commit guidelines.

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-10-01)


### 🚀 Features

* [deploy-all] add ALB host-based routing for web service and update backup script paths ([c93586c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c93586c71aaf0ec5d2376f38e6af0e1c433b7060))
* [deploy-all] add domain name to OpenSearch domain configuration ([5034be2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5034be297d8f90903d7406e81faf452997c1e7b7))
* [deploy-all] add environment-specific domain prefixing for ALB certificates- Add get_env_domains() function to prefix domains by environment- Dev: dev.domain.com, Staging: staging.domain.com, Prod: domain.com- Each environment gets its own ALB with environment-specific domains- Certificates are automatically created per domain with ACM DNS validationConfiguration:- Dev ALB: dev.049022.xyz, dev.049023.xyz, dev.04902{N}.xyz- Staging ALB: staging.049022.xyz, staging.049023.xyz, staging.04902{N}.xyz  - Prod ALB: 049022.xyz, 049023.xyz, 04902{N}.xyzThis enables proper multi-environment domain routing with shared base domains. ([659f088](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/659f08871027c6f3f4103e4d2b1678ea06ffb859))
* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add commit message trigger for multi-environment deployment ([09026d0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/09026d0f0479f45b2659dba524d79e183f131e5e))
* add configurable desired_count for ECS services and handle git tag conflicts ([81128b0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81128b0b37f3337ebca6e32aec1aba92c1432956))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* add multi-environment deployment support to workflows ([1c7ccfc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1c7ccfc5f6008a04dfb10a015d09cd5c2c8e8c39))
* add OpenSearch backup scripts and extend test coverage reporting ([ee0799d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ee0799dd63e86d6e8915d573c9b871986ef6ad3f))
* add scripts to migrate ECR repos from environment-specific to shared architecture ([a70503f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a70503fad8cb3549f7dcddfb2d07760632a182dc))
* add snapshot policy for database instance replacement with custom name ([e9f9dee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e9f9dee63ab90a212f7ad593565e923a9f48c4d6))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* [deploy-all] append environment to service names and remove duplicate env from CloudMap names ([28fbbf9](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fbbf9e8fabc09396bec135823dc41532dcf707))
* [deploy-all] update comment wording for ECR stack creation ([3e9649e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3e9649ed17e64c3468bd190b16b3ce2812ee9a56))
* [deploy-all] update DomainDnsStack to support environment-specific subdomains- Extract root zone from full domain name (cidertees.com from dev.cidertees.com)- Look up hosted zone using root domain instead of full subdomain- Create A records for actual domain (dev.cidertees.com, staging.cidertees.com, or cidertees.com)- Remove duplicate dev. prefix logicThis fixes the 'Found zones: [] for dns:dev.cidertees.com' error by correctlylooking up the root hosted zone and creating subdomain records within it. ([3553aff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3553aff7bb042e44c8ef3736591dd5bf00a7be8b))
* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* improve error handling for Bandit and Safety security scans by creating fallback reports ([2e8bde2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e8bde2d1313edad36e91d6fdeaf5cf94af743a5))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* remove unused parameters_stack import and add newline for code style ([b2182cc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b2182cce2956aedf845d9fad2ee9be0c0399f171))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* resolve workflow syntax error for commit message trigger ([1784d5b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1784d5b12f4434a69814cb499dac1bb01706b2a1))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use correct database name from secrets manager when backing up RDS instances ([ddc6beb](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ddc6bebec6b737625de6a56805dbdaf9f79c9633))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ⚡ Performance Improvements

* downgrade staging/prod infrastructure to reduce costs ([2d305a2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d305a26160e1a80726964678401219082cffe73))


### 📚 Documentation

* [deploy-all] update deployment instructions to use commit message trigger for multi-environment deploys ([f18fa5c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f18fa5c445b44543b334ed69214ff28e95124925))
* update multi-environment deployment guide and database configuration ([90f2bb7](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/90f2bb73991b4affbed585f8c9e1020d5a2d9ecc))


### ♻️ Code Refactoring

* [deploy-all] move docs and scripts to dedicated directories ([ec14543](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ec1454321c21f874b9e6a02cf05fbfdb9118ab8f))
* improve security scan workflow with better error handling and code formatting ([28fc8d5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fc8d50a2fac9fe3edd9a6d3d186e89e1d541d1))
* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* remove unused ParametersStack and related code ([62917c2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/62917c249c55a82275b0b033e68d07d22314dd02))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))
* use shared ECR repositories across all environments ([30d378b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/30d378baade2b4341436312caeebd00524bc2512))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-10-01)


### 🚀 Features

* [deploy-all] add ALB host-based routing for web service and update backup script paths ([c93586c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c93586c71aaf0ec5d2376f38e6af0e1c433b7060))
* [deploy-all] add domain name to OpenSearch domain configuration ([5034be2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5034be297d8f90903d7406e81faf452997c1e7b7))
* [deploy-all] add environment-specific domain prefixing for ALB certificates- Add get_env_domains() function to prefix domains by environment- Dev: dev.domain.com, Staging: staging.domain.com, Prod: domain.com- Each environment gets its own ALB with environment-specific domains- Certificates are automatically created per domain with ACM DNS validationConfiguration:- Dev ALB: dev.049022.xyz, dev.049023.xyz, dev.04902{N}.xyz- Staging ALB: staging.049022.xyz, staging.049023.xyz, staging.04902{N}.xyz  - Prod ALB: 049022.xyz, 049023.xyz, 04902{N}.xyzThis enables proper multi-environment domain routing with shared base domains. ([659f088](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/659f08871027c6f3f4103e4d2b1678ea06ffb859))
* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add commit message trigger for multi-environment deployment ([09026d0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/09026d0f0479f45b2659dba524d79e183f131e5e))
* add configurable desired_count for ECS services and handle git tag conflicts ([81128b0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81128b0b37f3337ebca6e32aec1aba92c1432956))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* add multi-environment deployment support to workflows ([1c7ccfc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1c7ccfc5f6008a04dfb10a015d09cd5c2c8e8c39))
* add OpenSearch backup scripts and extend test coverage reporting ([ee0799d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ee0799dd63e86d6e8915d573c9b871986ef6ad3f))
* add scripts to migrate ECR repos from environment-specific to shared architecture ([a70503f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a70503fad8cb3549f7dcddfb2d07760632a182dc))
* add snapshot policy for database instance replacement with custom name ([e9f9dee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e9f9dee63ab90a212f7ad593565e923a9f48c4d6))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* [deploy-all] append environment to service names and remove duplicate env from CloudMap names ([28fbbf9](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fbbf9e8fabc09396bec135823dc41532dcf707))
* [deploy-all] update comment wording for ECR stack creation ([3e9649e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3e9649ed17e64c3468bd190b16b3ce2812ee9a56))
* [deploy-all] update DomainDnsStack to support environment-specific subdomains- Extract root zone from full domain name (cidertees.com from dev.cidertees.com)- Look up hosted zone using root domain instead of full subdomain- Create A records for actual domain (dev.cidertees.com, staging.cidertees.com, or cidertees.com)- Remove duplicate dev. prefix logicThis fixes the 'Found zones: [] for dns:dev.cidertees.com' error by correctlylooking up the root hosted zone and creating subdomain records within it. ([3553aff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3553aff7bb042e44c8ef3736591dd5bf00a7be8b))
* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* improve error handling for Bandit and Safety security scans by creating fallback reports ([2e8bde2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e8bde2d1313edad36e91d6fdeaf5cf94af743a5))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* remove unused parameters_stack import and add newline for code style ([b2182cc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b2182cce2956aedf845d9fad2ee9be0c0399f171))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* resolve workflow syntax error for commit message trigger ([1784d5b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1784d5b12f4434a69814cb499dac1bb01706b2a1))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ⚡ Performance Improvements

* downgrade staging/prod infrastructure to reduce costs ([2d305a2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d305a26160e1a80726964678401219082cffe73))


### 📚 Documentation

* [deploy-all] update deployment instructions to use commit message trigger for multi-environment deploys ([f18fa5c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f18fa5c445b44543b334ed69214ff28e95124925))
* update multi-environment deployment guide and database configuration ([90f2bb7](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/90f2bb73991b4affbed585f8c9e1020d5a2d9ecc))


### ♻️ Code Refactoring

* [deploy-all] move docs and scripts to dedicated directories ([ec14543](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ec1454321c21f874b9e6a02cf05fbfdb9118ab8f))
* improve security scan workflow with better error handling and code formatting ([28fc8d5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fc8d50a2fac9fe3edd9a6d3d186e89e1d541d1))
* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* remove unused ParametersStack and related code ([62917c2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/62917c249c55a82275b0b033e68d07d22314dd02))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))
* use shared ECR repositories across all environments ([30d378b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/30d378baade2b4341436312caeebd00524bc2512))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-10-01)


### 🚀 Features

* [deploy-all] add domain name to OpenSearch domain configuration ([5034be2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5034be297d8f90903d7406e81faf452997c1e7b7))
* [deploy-all] add environment-specific domain prefixing for ALB certificates- Add get_env_domains() function to prefix domains by environment- Dev: dev.domain.com, Staging: staging.domain.com, Prod: domain.com- Each environment gets its own ALB with environment-specific domains- Certificates are automatically created per domain with ACM DNS validationConfiguration:- Dev ALB: dev.049022.xyz, dev.049023.xyz, dev.04902{N}.xyz- Staging ALB: staging.049022.xyz, staging.049023.xyz, staging.04902{N}.xyz  - Prod ALB: 049022.xyz, 049023.xyz, 04902{N}.xyzThis enables proper multi-environment domain routing with shared base domains. ([659f088](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/659f08871027c6f3f4103e4d2b1678ea06ffb859))
* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add commit message trigger for multi-environment deployment ([09026d0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/09026d0f0479f45b2659dba524d79e183f131e5e))
* add configurable desired_count for ECS services and handle git tag conflicts ([81128b0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81128b0b37f3337ebca6e32aec1aba92c1432956))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* add multi-environment deployment support to workflows ([1c7ccfc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1c7ccfc5f6008a04dfb10a015d09cd5c2c8e8c39))
* add OpenSearch backup scripts and extend test coverage reporting ([ee0799d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ee0799dd63e86d6e8915d573c9b871986ef6ad3f))
* add scripts to migrate ECR repos from environment-specific to shared architecture ([a70503f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a70503fad8cb3549f7dcddfb2d07760632a182dc))
* add snapshot policy for database instance replacement with custom name ([e9f9dee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e9f9dee63ab90a212f7ad593565e923a9f48c4d6))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* [deploy-all] append environment to service names and remove duplicate env from CloudMap names ([28fbbf9](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fbbf9e8fabc09396bec135823dc41532dcf707))
* [deploy-all] update comment wording for ECR stack creation ([3e9649e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3e9649ed17e64c3468bd190b16b3ce2812ee9a56))
* [deploy-all] update DomainDnsStack to support environment-specific subdomains- Extract root zone from full domain name (cidertees.com from dev.cidertees.com)- Look up hosted zone using root domain instead of full subdomain- Create A records for actual domain (dev.cidertees.com, staging.cidertees.com, or cidertees.com)- Remove duplicate dev. prefix logicThis fixes the 'Found zones: [] for dns:dev.cidertees.com' error by correctlylooking up the root hosted zone and creating subdomain records within it. ([3553aff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3553aff7bb042e44c8ef3736591dd5bf00a7be8b))
* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* improve error handling for Bandit and Safety security scans by creating fallback reports ([2e8bde2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e8bde2d1313edad36e91d6fdeaf5cf94af743a5))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* remove unused parameters_stack import and add newline for code style ([b2182cc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b2182cce2956aedf845d9fad2ee9be0c0399f171))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* resolve workflow syntax error for commit message trigger ([1784d5b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1784d5b12f4434a69814cb499dac1bb01706b2a1))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ⚡ Performance Improvements

* downgrade staging/prod infrastructure to reduce costs ([2d305a2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d305a26160e1a80726964678401219082cffe73))


### 📚 Documentation

* [deploy-all] update deployment instructions to use commit message trigger for multi-environment deploys ([f18fa5c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f18fa5c445b44543b334ed69214ff28e95124925))
* update multi-environment deployment guide and database configuration ([90f2bb7](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/90f2bb73991b4affbed585f8c9e1020d5a2d9ecc))


### ♻️ Code Refactoring

* [deploy-all] move docs and scripts to dedicated directories ([ec14543](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ec1454321c21f874b9e6a02cf05fbfdb9118ab8f))
* improve security scan workflow with better error handling and code formatting ([28fc8d5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fc8d50a2fac9fe3edd9a6d3d186e89e1d541d1))
* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* remove unused ParametersStack and related code ([62917c2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/62917c249c55a82275b0b033e68d07d22314dd02))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))
* use shared ECR repositories across all environments ([30d378b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/30d378baade2b4341436312caeebd00524bc2512))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-10-01)


### 🚀 Features

* [deploy-all] add domain name to OpenSearch domain configuration ([5034be2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5034be297d8f90903d7406e81faf452997c1e7b7))
* [deploy-all] add environment-specific domain prefixing for ALB certificates- Add get_env_domains() function to prefix domains by environment- Dev: dev.domain.com, Staging: staging.domain.com, Prod: domain.com- Each environment gets its own ALB with environment-specific domains- Certificates are automatically created per domain with ACM DNS validationConfiguration:- Dev ALB: dev.049022.xyz, dev.049023.xyz, dev.04902{N}.xyz- Staging ALB: staging.049022.xyz, staging.049023.xyz, staging.04902{N}.xyz  - Prod ALB: 049022.xyz, 049023.xyz, 04902{N}.xyzThis enables proper multi-environment domain routing with shared base domains. ([659f088](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/659f08871027c6f3f4103e4d2b1678ea06ffb859))
* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add commit message trigger for multi-environment deployment ([09026d0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/09026d0f0479f45b2659dba524d79e183f131e5e))
* add configurable desired_count for ECS services and handle git tag conflicts ([81128b0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81128b0b37f3337ebca6e32aec1aba92c1432956))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* add multi-environment deployment support to workflows ([1c7ccfc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1c7ccfc5f6008a04dfb10a015d09cd5c2c8e8c39))
* add OpenSearch backup scripts and extend test coverage reporting ([ee0799d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ee0799dd63e86d6e8915d573c9b871986ef6ad3f))
* add scripts to migrate ECR repos from environment-specific to shared architecture ([a70503f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a70503fad8cb3549f7dcddfb2d07760632a182dc))
* add snapshot policy for database instance replacement with custom name ([e9f9dee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e9f9dee63ab90a212f7ad593565e923a9f48c4d6))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* [deploy-all] append environment to service names and remove duplicate env from CloudMap names ([28fbbf9](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fbbf9e8fabc09396bec135823dc41532dcf707))
* [deploy-all] update comment wording for ECR stack creation ([3e9649e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3e9649ed17e64c3468bd190b16b3ce2812ee9a56))
* [deploy-all] update DomainDnsStack to support environment-specific subdomains- Extract root zone from full domain name (cidertees.com from dev.cidertees.com)- Look up hosted zone using root domain instead of full subdomain- Create A records for actual domain (dev.cidertees.com, staging.cidertees.com, or cidertees.com)- Remove duplicate dev. prefix logicThis fixes the 'Found zones: [] for dns:dev.cidertees.com' error by correctlylooking up the root hosted zone and creating subdomain records within it. ([3553aff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3553aff7bb042e44c8ef3736591dd5bf00a7be8b))
* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* improve error handling for Bandit and Safety security scans by creating fallback reports ([2e8bde2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e8bde2d1313edad36e91d6fdeaf5cf94af743a5))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* remove unused parameters_stack import and add newline for code style ([b2182cc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b2182cce2956aedf845d9fad2ee9be0c0399f171))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* resolve workflow syntax error for commit message trigger ([1784d5b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1784d5b12f4434a69814cb499dac1bb01706b2a1))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ⚡ Performance Improvements

* downgrade staging/prod infrastructure to reduce costs ([2d305a2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d305a26160e1a80726964678401219082cffe73))


### 📚 Documentation

* [deploy-all] update deployment instructions to use commit message trigger for multi-environment deploys ([f18fa5c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f18fa5c445b44543b334ed69214ff28e95124925))


### ♻️ Code Refactoring

* [deploy-all] move docs and scripts to dedicated directories ([ec14543](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ec1454321c21f874b9e6a02cf05fbfdb9118ab8f))
* improve security scan workflow with better error handling and code formatting ([28fc8d5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fc8d50a2fac9fe3edd9a6d3d186e89e1d541d1))
* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* remove unused ParametersStack and related code ([62917c2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/62917c249c55a82275b0b033e68d07d22314dd02))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))
* use shared ECR repositories across all environments ([30d378b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/30d378baade2b4341436312caeebd00524bc2512))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-30)


### 🚀 Features

* [deploy-all] add domain name to OpenSearch domain configuration ([5034be2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5034be297d8f90903d7406e81faf452997c1e7b7))
* [deploy-all] add environment-specific domain prefixing for ALB certificates- Add get_env_domains() function to prefix domains by environment- Dev: dev.domain.com, Staging: staging.domain.com, Prod: domain.com- Each environment gets its own ALB with environment-specific domains- Certificates are automatically created per domain with ACM DNS validationConfiguration:- Dev ALB: dev.049022.xyz, dev.049023.xyz, dev.04902{N}.xyz- Staging ALB: staging.049022.xyz, staging.049023.xyz, staging.04902{N}.xyz  - Prod ALB: 049022.xyz, 049023.xyz, 04902{N}.xyzThis enables proper multi-environment domain routing with shared base domains. ([659f088](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/659f08871027c6f3f4103e4d2b1678ea06ffb859))
* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add commit message trigger for multi-environment deployment ([09026d0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/09026d0f0479f45b2659dba524d79e183f131e5e))
* add configurable desired_count for ECS services and handle git tag conflicts ([81128b0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81128b0b37f3337ebca6e32aec1aba92c1432956))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* add multi-environment deployment support to workflows ([1c7ccfc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1c7ccfc5f6008a04dfb10a015d09cd5c2c8e8c39))
* add scripts to migrate ECR repos from environment-specific to shared architecture ([a70503f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a70503fad8cb3549f7dcddfb2d07760632a182dc))
* add snapshot policy for database instance replacement with custom name ([e9f9dee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e9f9dee63ab90a212f7ad593565e923a9f48c4d6))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* [deploy-all] update comment wording for ECR stack creation ([3e9649e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3e9649ed17e64c3468bd190b16b3ce2812ee9a56))
* [deploy-all] update DomainDnsStack to support environment-specific subdomains- Extract root zone from full domain name (cidertees.com from dev.cidertees.com)- Look up hosted zone using root domain instead of full subdomain- Create A records for actual domain (dev.cidertees.com, staging.cidertees.com, or cidertees.com)- Remove duplicate dev. prefix logicThis fixes the 'Found zones: [] for dns:dev.cidertees.com' error by correctlylooking up the root hosted zone and creating subdomain records within it. ([3553aff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3553aff7bb042e44c8ef3736591dd5bf00a7be8b))
* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* improve error handling for Bandit and Safety security scans by creating fallback reports ([2e8bde2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e8bde2d1313edad36e91d6fdeaf5cf94af743a5))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* remove unused parameters_stack import and add newline for code style ([b2182cc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b2182cce2956aedf845d9fad2ee9be0c0399f171))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* resolve workflow syntax error for commit message trigger ([1784d5b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1784d5b12f4434a69814cb499dac1bb01706b2a1))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ⚡ Performance Improvements

* downgrade staging/prod infrastructure to reduce costs ([2d305a2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d305a26160e1a80726964678401219082cffe73))


### ♻️ Code Refactoring

* [deploy-all] move docs and scripts to dedicated directories ([ec14543](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ec1454321c21f874b9e6a02cf05fbfdb9118ab8f))
* improve security scan workflow with better error handling and code formatting ([28fc8d5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fc8d50a2fac9fe3edd9a6d3d186e89e1d541d1))
* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* remove unused ParametersStack and related code ([62917c2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/62917c249c55a82275b0b033e68d07d22314dd02))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))
* use shared ECR repositories across all environments ([30d378b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/30d378baade2b4341436312caeebd00524bc2512))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-30)


### 🚀 Features

* [deploy-all] add domain name to OpenSearch domain configuration ([5034be2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5034be297d8f90903d7406e81faf452997c1e7b7))
* [deploy-all] add environment-specific domain prefixing for ALB certificates- Add get_env_domains() function to prefix domains by environment- Dev: dev.domain.com, Staging: staging.domain.com, Prod: domain.com- Each environment gets its own ALB with environment-specific domains- Certificates are automatically created per domain with ACM DNS validationConfiguration:- Dev ALB: dev.049022.xyz, dev.049023.xyz, dev.04902{N}.xyz- Staging ALB: staging.049022.xyz, staging.049023.xyz, staging.04902{N}.xyz  - Prod ALB: 049022.xyz, 049023.xyz, 04902{N}.xyzThis enables proper multi-environment domain routing with shared base domains. ([659f088](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/659f08871027c6f3f4103e4d2b1678ea06ffb859))
* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add commit message trigger for multi-environment deployment ([09026d0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/09026d0f0479f45b2659dba524d79e183f131e5e))
* add configurable desired_count for ECS services and handle git tag conflicts ([81128b0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81128b0b37f3337ebca6e32aec1aba92c1432956))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* add multi-environment deployment support to workflows ([1c7ccfc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1c7ccfc5f6008a04dfb10a015d09cd5c2c8e8c39))
* add scripts to migrate ECR repos from environment-specific to shared architecture ([a70503f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a70503fad8cb3549f7dcddfb2d07760632a182dc))
* add snapshot policy for database instance replacement with custom name ([e9f9dee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e9f9dee63ab90a212f7ad593565e923a9f48c4d6))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* [deploy-all] update comment wording for ECR stack creation ([3e9649e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3e9649ed17e64c3468bd190b16b3ce2812ee9a56))
* [deploy-all] update DomainDnsStack to support environment-specific subdomains- Extract root zone from full domain name (cidertees.com from dev.cidertees.com)- Look up hosted zone using root domain instead of full subdomain- Create A records for actual domain (dev.cidertees.com, staging.cidertees.com, or cidertees.com)- Remove duplicate dev. prefix logicThis fixes the 'Found zones: [] for dns:dev.cidertees.com' error by correctlylooking up the root hosted zone and creating subdomain records within it. ([3553aff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3553aff7bb042e44c8ef3736591dd5bf00a7be8b))
* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* improve error handling for Bandit and Safety security scans by creating fallback reports ([2e8bde2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e8bde2d1313edad36e91d6fdeaf5cf94af743a5))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* remove unused parameters_stack import and add newline for code style ([b2182cc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b2182cce2956aedf845d9fad2ee9be0c0399f171))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* resolve workflow syntax error for commit message trigger ([1784d5b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1784d5b12f4434a69814cb499dac1bb01706b2a1))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ⚡ Performance Improvements

* downgrade staging/prod infrastructure to reduce costs ([2d305a2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d305a26160e1a80726964678401219082cffe73))


### ♻️ Code Refactoring

* improve security scan workflow with better error handling and code formatting ([28fc8d5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fc8d50a2fac9fe3edd9a6d3d186e89e1d541d1))
* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* remove unused ParametersStack and related code ([62917c2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/62917c249c55a82275b0b033e68d07d22314dd02))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))
* use shared ECR repositories across all environments ([30d378b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/30d378baade2b4341436312caeebd00524bc2512))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-30)


### 🚀 Features

* [deploy-all] add environment-specific domain prefixing for ALB certificates- Add get_env_domains() function to prefix domains by environment- Dev: dev.domain.com, Staging: staging.domain.com, Prod: domain.com- Each environment gets its own ALB with environment-specific domains- Certificates are automatically created per domain with ACM DNS validationConfiguration:- Dev ALB: dev.049022.xyz, dev.049023.xyz, dev.04902{N}.xyz- Staging ALB: staging.049022.xyz, staging.049023.xyz, staging.04902{N}.xyz  - Prod ALB: 049022.xyz, 049023.xyz, 04902{N}.xyzThis enables proper multi-environment domain routing with shared base domains. ([659f088](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/659f08871027c6f3f4103e4d2b1678ea06ffb859))
* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add commit message trigger for multi-environment deployment ([09026d0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/09026d0f0479f45b2659dba524d79e183f131e5e))
* add configurable desired_count for ECS services and handle git tag conflicts ([81128b0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81128b0b37f3337ebca6e32aec1aba92c1432956))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* add multi-environment deployment support to workflows ([1c7ccfc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1c7ccfc5f6008a04dfb10a015d09cd5c2c8e8c39))
* add scripts to migrate ECR repos from environment-specific to shared architecture ([a70503f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a70503fad8cb3549f7dcddfb2d07760632a182dc))
* add snapshot policy for database instance replacement with custom name ([e9f9dee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e9f9dee63ab90a212f7ad593565e923a9f48c4d6))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* [deploy-all] update comment wording for ECR stack creation ([3e9649e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3e9649ed17e64c3468bd190b16b3ce2812ee9a56))
* [deploy-all] update DomainDnsStack to support environment-specific subdomains- Extract root zone from full domain name (cidertees.com from dev.cidertees.com)- Look up hosted zone using root domain instead of full subdomain- Create A records for actual domain (dev.cidertees.com, staging.cidertees.com, or cidertees.com)- Remove duplicate dev. prefix logicThis fixes the 'Found zones: [] for dns:dev.cidertees.com' error by correctlylooking up the root hosted zone and creating subdomain records within it. ([3553aff](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3553aff7bb042e44c8ef3736591dd5bf00a7be8b))
* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* improve error handling for Bandit and Safety security scans by creating fallback reports ([2e8bde2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e8bde2d1313edad36e91d6fdeaf5cf94af743a5))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* remove unused parameters_stack import and add newline for code style ([b2182cc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b2182cce2956aedf845d9fad2ee9be0c0399f171))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* resolve workflow syntax error for commit message trigger ([1784d5b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1784d5b12f4434a69814cb499dac1bb01706b2a1))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ⚡ Performance Improvements

* downgrade staging/prod infrastructure to reduce costs ([2d305a2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d305a26160e1a80726964678401219082cffe73))


### ♻️ Code Refactoring

* improve security scan workflow with better error handling and code formatting ([28fc8d5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fc8d50a2fac9fe3edd9a6d3d186e89e1d541d1))
* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* remove unused ParametersStack and related code ([62917c2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/62917c249c55a82275b0b033e68d07d22314dd02))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))
* use shared ECR repositories across all environments ([30d378b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/30d378baade2b4341436312caeebd00524bc2512))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-30)


### 🚀 Features

* [deploy-all] add environment-specific domain prefixing for ALB certificates- Add get_env_domains() function to prefix domains by environment- Dev: dev.domain.com, Staging: staging.domain.com, Prod: domain.com- Each environment gets its own ALB with environment-specific domains- Certificates are automatically created per domain with ACM DNS validationConfiguration:- Dev ALB: dev.049022.xyz, dev.049023.xyz, dev.04902{N}.xyz- Staging ALB: staging.049022.xyz, staging.049023.xyz, staging.04902{N}.xyz  - Prod ALB: 049022.xyz, 049023.xyz, 04902{N}.xyzThis enables proper multi-environment domain routing with shared base domains. ([659f088](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/659f08871027c6f3f4103e4d2b1678ea06ffb859))
* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add commit message trigger for multi-environment deployment ([09026d0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/09026d0f0479f45b2659dba524d79e183f131e5e))
* add configurable desired_count for ECS services and handle git tag conflicts ([81128b0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81128b0b37f3337ebca6e32aec1aba92c1432956))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* add multi-environment deployment support to workflows ([1c7ccfc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1c7ccfc5f6008a04dfb10a015d09cd5c2c8e8c39))
* add scripts to migrate ECR repos from environment-specific to shared architecture ([a70503f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a70503fad8cb3549f7dcddfb2d07760632a182dc))
* add snapshot policy for database instance replacement with custom name ([e9f9dee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e9f9dee63ab90a212f7ad593565e923a9f48c4d6))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* [deploy-all] update comment wording for ECR stack creation ([3e9649e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3e9649ed17e64c3468bd190b16b3ce2812ee9a56))
* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* improve error handling for Bandit and Safety security scans by creating fallback reports ([2e8bde2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e8bde2d1313edad36e91d6fdeaf5cf94af743a5))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* remove unused parameters_stack import and add newline for code style ([b2182cc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b2182cce2956aedf845d9fad2ee9be0c0399f171))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* resolve workflow syntax error for commit message trigger ([1784d5b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1784d5b12f4434a69814cb499dac1bb01706b2a1))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ⚡ Performance Improvements

* downgrade staging/prod infrastructure to reduce costs ([2d305a2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d305a26160e1a80726964678401219082cffe73))


### ♻️ Code Refactoring

* improve security scan workflow with better error handling and code formatting ([28fc8d5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fc8d50a2fac9fe3edd9a6d3d186e89e1d541d1))
* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* remove unused ParametersStack and related code ([62917c2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/62917c249c55a82275b0b033e68d07d22314dd02))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))
* use shared ECR repositories across all environments ([30d378b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/30d378baade2b4341436312caeebd00524bc2512))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-30)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add commit message trigger for multi-environment deployment ([09026d0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/09026d0f0479f45b2659dba524d79e183f131e5e))
* add configurable desired_count for ECS services and handle git tag conflicts ([81128b0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81128b0b37f3337ebca6e32aec1aba92c1432956))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* add multi-environment deployment support to workflows ([1c7ccfc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1c7ccfc5f6008a04dfb10a015d09cd5c2c8e8c39))
* add scripts to migrate ECR repos from environment-specific to shared architecture ([a70503f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a70503fad8cb3549f7dcddfb2d07760632a182dc))
* add snapshot policy for database instance replacement with custom name ([e9f9dee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e9f9dee63ab90a212f7ad593565e923a9f48c4d6))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* improve error handling for Bandit and Safety security scans by creating fallback reports ([2e8bde2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e8bde2d1313edad36e91d6fdeaf5cf94af743a5))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* remove unused parameters_stack import and add newline for code style ([b2182cc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b2182cce2956aedf845d9fad2ee9be0c0399f171))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* resolve workflow syntax error for commit message trigger ([1784d5b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1784d5b12f4434a69814cb499dac1bb01706b2a1))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ⚡ Performance Improvements

* downgrade staging/prod infrastructure to reduce costs ([2d305a2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d305a26160e1a80726964678401219082cffe73))


### ♻️ Code Refactoring

* improve security scan workflow with better error handling and code formatting ([28fc8d5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fc8d50a2fac9fe3edd9a6d3d186e89e1d541d1))
* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* remove unused ParametersStack and related code ([62917c2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/62917c249c55a82275b0b033e68d07d22314dd02))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))
* use shared ECR repositories across all environments ([30d378b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/30d378baade2b4341436312caeebd00524bc2512))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-30)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add commit message trigger for multi-environment deployment ([09026d0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/09026d0f0479f45b2659dba524d79e183f131e5e))
* add configurable desired_count for ECS services and handle git tag conflicts ([81128b0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81128b0b37f3337ebca6e32aec1aba92c1432956))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* add multi-environment deployment support to workflows ([1c7ccfc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1c7ccfc5f6008a04dfb10a015d09cd5c2c8e8c39))
* add snapshot policy for database instance replacement with custom name ([e9f9dee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e9f9dee63ab90a212f7ad593565e923a9f48c4d6))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* improve error handling for Bandit and Safety security scans by creating fallback reports ([2e8bde2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e8bde2d1313edad36e91d6fdeaf5cf94af743a5))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* resolve workflow syntax error for commit message trigger ([1784d5b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1784d5b12f4434a69814cb499dac1bb01706b2a1))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ⚡ Performance Improvements

* downgrade staging/prod infrastructure to reduce costs ([2d305a2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d305a26160e1a80726964678401219082cffe73))


### ♻️ Code Refactoring

* improve security scan workflow with better error handling and code formatting ([28fc8d5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fc8d50a2fac9fe3edd9a6d3d186e89e1d541d1))
* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-30)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add configurable desired_count for ECS services and handle git tag conflicts ([81128b0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81128b0b37f3337ebca6e32aec1aba92c1432956))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* add multi-environment deployment support to workflows ([1c7ccfc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1c7ccfc5f6008a04dfb10a015d09cd5c2c8e8c39))
* add snapshot policy for database instance replacement with custom name ([e9f9dee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e9f9dee63ab90a212f7ad593565e923a9f48c4d6))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* improve error handling for Bandit and Safety security scans by creating fallback reports ([2e8bde2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e8bde2d1313edad36e91d6fdeaf5cf94af743a5))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ⚡ Performance Improvements

* downgrade staging/prod infrastructure to reduce costs ([2d305a2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d305a26160e1a80726964678401219082cffe73))


### ♻️ Code Refactoring

* improve security scan workflow with better error handling and code formatting ([28fc8d5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fc8d50a2fac9fe3edd9a6d3d186e89e1d541d1))
* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-30)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* add multi-environment deployment support to workflows ([1c7ccfc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1c7ccfc5f6008a04dfb10a015d09cd5c2c8e8c39))
* add snapshot policy for database instance replacement with custom name ([e9f9dee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e9f9dee63ab90a212f7ad593565e923a9f48c4d6))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* improve error handling for Bandit and Safety security scans by creating fallback reports ([2e8bde2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e8bde2d1313edad36e91d6fdeaf5cf94af743a5))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ⚡ Performance Improvements

* downgrade staging/prod infrastructure to reduce costs ([2d305a2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d305a26160e1a80726964678401219082cffe73))


### ♻️ Code Refactoring

* improve security scan workflow with better error handling and code formatting ([28fc8d5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/28fc8d50a2fac9fe3edd9a6d3d186e89e1d541d1))
* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-29)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* add snapshot policy for database instance replacement with custom name ([e9f9dee](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e9f9dee63ab90a212f7ad593565e923a9f48c4d6))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-29)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* prevent duplicate test runs by removing push trigger ([987cc20](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/987cc2029da0ed9eb7030e05a93bf6c54c9f01c5))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-29)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain helper functions import for tenant resolution ([16e4754](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/16e4754b2ddf8e7c969d5784d1739440d8961bad))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add GitHub Actions workflows for staging and production deployments ([a983a74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a983a742a15370db305c8b8909df7b5d15fbad10))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* disable environment-dependent tests until staging/prod exist ([bf01e02](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf01e020a1e85fa5726f6c00393cf9ba30f1a5ee))
* disable staging deployment until environment exists ([f17fa9c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f17fa9ce9a2aca245b5baea7a8c7fe488fcc07e1))
* ensure security scans create valid JSON reports even on failure and auto-apply AWS mocks in tests ([a49fa5f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a49fa5f275ada61a22a45c14afb7ae0ea979bd64))
* format code with black and isort ([1de9e39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1de9e39eb69a03b39aca809609a141b9f514a71a))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve black/isort conflict with proper configuration ([81e8b87](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/81e8b87d457cbfe13ff6efd0cfa5df6e08c0fc87))
* resolve black/isort formatting conflicts and add concurrency ([c3b6f80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3b6f80d7506db9539dd49bdab4e5d333fcaa3e6))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* resolve env context issue in semantic-release workflow ([c42322f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c42322fa2a4303dd5fa102708d93108444596575))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* simplify deploy-infrastructure job dependencies and conditions ([b7b7654](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7b7654b14467295e66416b36c38da5a68431dc1))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-29)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* add database connection recovery to DNS worker ([1accf13](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1accf1383b5068d51b8d2f8e4f49c27068a14eb2))
* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-29)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* implement efficient delta-based DNS record management ([9ec737a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ec737adf0af3d7bfcb88b59e5217abac1028272))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-29)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* make deployment summary environment-aware ([128b888](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/128b8886c1fe376cd6990a0adcb7bb4e37956322))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-29)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))
* upgrade Lambda runtime to Python 3.11 and replace cfnresponse with direct JSON responses ([ab3be39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ab3be39a49446083de2614034549a2051d46caa4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* force Route53 record updates by adding timestamp to custom resource props ([96477e6](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/96477e6c82737e48b37d5bfd4739ef96e14f857d))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* correct auto-merge condition for domain-updates branch ([744469e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/744469e2790dff327fb61c628f5b202bb294452d))
* correct change detection flags for domain-updates branch ([a65a546](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a65a54694f7bea621cf29bad3ed62560e3ecfbcb))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* temporarily disable hosted zone deletion while keeping record cleanup ([901dffc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/901dffc0fff18ed9b8ef8b9f7b5b1f2bf17fa9e3))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* resolve concurrency deadlock between workflows ([72a13e3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72a13e3057861d48cc047ddd13024610be7cd36e))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move branch cleanup to workflow instead of DNS worker ([8859ece](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8859ece0d0f436b8c21253f327b559f1c3195e3d))
* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* align concurrency groups to prevent simultaneous infrastructure deployments ([a16e510](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a16e510d5fbaf4de8b611d132c0d28116db0eea1))
* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* delete and recreate domain-updates branch for clean deployments ([7b42094](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b420947dcd74b0f7e561af2f98ae8f0adc65b38))
* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* update tag resolver to fetch API/WEB tags from storefront-cdk repository ([2e3314e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e3314e458d8ec7109956af57786698d4afe565e))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))
* use latest tags instead of 'unchanged' for domain-updates branch ([1755172](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/175517232277fb8806661049739513ffa177715d))


### ♻️ Code Refactoring

* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))


### ♻️ Code Refactoring

* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))
* switch to parameter names instead of direct values for OpenSearch and SQS endpoints ([10fa27a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/10fa27ab917aef2867d2483444a0fdefe354adc4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))


### ♻️ Code Refactoring

* move domain_helpers.py into dns-worker app directory ([4232b2c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4232b2cbc7cfa0ae3aefcac4ef1b86babbabf643))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add domain_helpers import from listener directory to dns-worker Dockerfile ([ef58820](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ef58820008bf85ea78c735795d4f7a87ef6ae5c7))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add atomic domain activation/deactivation with hosted zone management ([5925173](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/592517375f3dd504332446931e7f5ea899f6fd76))
* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))


### 🐛 Bug Fixes

* rename deactivation_date to inactivation_date and add DeleteHostedZone IAM permission ([3356464](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/33564646e9f6b69bd13e8030364f9cde00d2f9f4))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* add hosted zone configuration for 042322.xyz domain ([d3f4a01](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f4a0137b4e543d4b3afbbb9caf4e8316fa1ce7))
* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))

## [1.76.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.2...v1.76.0) (2025-09-27)


### 🚀 Features

* update deployment summary to show individual service tags and add Route53 permissions ([002e5ba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/002e5ba7930898c624885317633983ad23107fdc))

## [1.75.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.1...v1.75.2) (2025-09-27)


### ♻️ Code Refactoring

* split shared requirements.txt into separate files for listener and dns-worker services ([0564bea](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/0564bea01274ce2cf389451cdfefabbca00e3b59))

## [1.75.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.75.0...v1.75.1) (2025-09-27)


### ♻️ Code Refactoring

* split monolithic Dockerfile into separate service-specific files ([c80ddf1](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c80ddf14dbe5bb0620f98d081441b864446170d7))

## [1.75.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.74.4...v1.75.0) (2025-09-27)


### 🚀 Features

* add empty tag_resolver.py file for future tag resolution implementation ([2625f16](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2625f16ded9638fb9485aac98d1a0c2f258a394b))

## [1.75.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.74.4...v1.75.0) (2025-09-27)


### 🚀 Features

* add empty tag_resolver.py file for future tag resolution implementation ([2625f16](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2625f16ded9638fb9485aac98d1a0c2f258a394b))

## [1.74.4](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.74.3...v1.74.4) (2025-09-27)


### ♻️ Code Refactoring

* improve tag resolver comments and error handling clarity ([d0c960b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d0c960b94d989bbe5731310c4728ca3d5cfdf976))

## [1.74.3](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.74.2...v1.74.3) (2025-09-27)


### ♻️ Code Refactoring

* improve change detection logic in CI/CD workflow and remove domain-updates branch cleanup ([b749bb8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b749bb867b65b4a3942688e6652d9ef04510bc98))
* simplify change detection logic and improve domain updates workflow ([44e1bbf](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/44e1bbf8fb2be7db53a9dd0d6bd19bf63007c78d))

## [1.74.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.74.0...v1.74.1) (2025-09-26)


### 🐛 Bug Fixes

* simplify comment about installing dependencies in Dockerfile ([8ac887f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8ac887ff08433553093d44b0ccebe48aa1fd9d23))
* update output variable names in semantic release workflow ([bb97863](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bb97863f58072739f1cdf475173d3a18edeef336))


### ♻️ Code Refactoring

* enhance change detection logic and deployment workflow with improved error handling ([155e5d7](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/155e5d71bea2d1eb8d40aba2ade0a516d758d4ba))
* simplify workflow with improved change detection and tag generation logic ([562b388](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/562b3886a8a9e073c3a1e592ee6d457d3567e25b))

## [1.74.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.74.0...v1.74.1) (2025-09-26)


### 🐛 Bug Fixes

* simplify comment about installing dependencies in Dockerfile ([8ac887f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8ac887ff08433553093d44b0ccebe48aa1fd9d23))


### ♻️ Code Refactoring

* enhance change detection logic and deployment workflow with improved error handling ([155e5d7](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/155e5d71bea2d1eb8d40aba2ade0a516d758d4ba))
* simplify workflow with improved change detection and tag generation logic ([562b388](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/562b3886a8a9e073c3a1e592ee6d457d3567e25b))

## [1.74.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.74.0...v1.74.1) (2025-09-26)


### 🐛 Bug Fixes

* simplify comment about installing dependencies in Dockerfile ([8ac887f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8ac887ff08433553093d44b0ccebe48aa1fd9d23))


### ♻️ Code Refactoring

* simplify workflow with improved change detection and tag generation logic ([562b388](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/562b3886a8a9e073c3a1e592ee6d457d3567e25b))

## [1.74.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.74.0...v1.74.1) (2025-09-26)


### 🐛 Bug Fixes

* simplify comment about installing dependencies in Dockerfile ([8ac887f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8ac887ff08433553093d44b0ccebe48aa1fd9d23))

## [1.74.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.73.0...v1.74.0) (2025-09-26)


### 🚀 Features

* add email DNS configuration and domain deactivation support ([e6ba140](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e6ba14054a8a4c72618dd9bfccd5fc9dac87d479))


### 🐛 Bug Fixes

* update domains list and clarify listener setup comment ([0e93719](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/0e937192e32331f29475b683afbe7f444acd4e99))


### ♻️ Code Refactoring

* extract infra paths pattern into variable and remove redundant logging ([5c1f9fd](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5c1f9fd14fed90604681507ce1681d31eae50646))
* implement idempotent Route53 record management with custom Lambda resource ([1764b39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1764b399523cfe2b750b02048f17abd9bdfe3555))
* simplify CI workflows and add git tagging for successful builds ([8559e03](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8559e031651a930f7ceb32a04e93d5955d566c55))
* standardize version tag resolution using service-specific prefixes ([7b81aaf](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7b81aaf6f73ab935bc1adf9ee28bd1aaaadc84e9))

## [1.74.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.73.0...v1.74.0) (2025-09-26)


### 🚀 Features

* add email DNS configuration and domain deactivation support ([e6ba140](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e6ba14054a8a4c72618dd9bfccd5fc9dac87d479))


### 🐛 Bug Fixes

* update domains list and clarify listener setup comment ([0e93719](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/0e937192e32331f29475b683afbe7f444acd4e99))


### ♻️ Code Refactoring

* implement idempotent Route53 record management with custom Lambda resource ([1764b39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1764b399523cfe2b750b02048f17abd9bdfe3555))
* simplify CI workflows and add git tagging for successful builds ([8559e03](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8559e031651a930f7ceb32a04e93d5955d566c55))

## [1.74.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.73.0...v1.74.0) (2025-09-26)


### 🚀 Features

* add email DNS configuration and domain deactivation support ([e6ba140](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e6ba14054a8a4c72618dd9bfccd5fc9dac87d479))


### 🐛 Bug Fixes

* update domains list and clarify listener setup comment ([0e93719](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/0e937192e32331f29475b683afbe7f444acd4e99))


### ♻️ Code Refactoring

* implement idempotent Route53 record management with custom Lambda resource ([1764b39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1764b399523cfe2b750b02048f17abd9bdfe3555))

## [1.74.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.73.0...v1.74.0) (2025-09-26)


### 🚀 Features

* add email DNS configuration and domain deactivation support ([e6ba140](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e6ba14054a8a4c72618dd9bfccd5fc9dac87d479))


### ♻️ Code Refactoring

* implement idempotent Route53 record management with custom Lambda resource ([1764b39](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1764b399523cfe2b750b02048f17abd9bdfe3555))

## [1.74.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.73.0...v1.74.0) (2025-09-26)


### 🚀 Features

* add email DNS configuration and domain deactivation support ([e6ba140](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e6ba14054a8a4c72618dd9bfccd5fc9dac87d479))

## [1.73.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.72.2...v1.73.0) (2025-09-26)


### 🚀 Features

* use latest git tag for deployment version instead of hardcoded v1.0.0 ([56e72a1](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/56e72a185e6e51cd750fd065b2343205fede0b34))

## [1.72.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.72.1...v1.72.2) (2025-09-26)


### ♻️ Code Refactoring

* simplify tag resolution logic by removing external repo handling and file dependencies ([6495028](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/64950284e3fc8380066feb15ce88c824d2ce1b06))

## [1.72.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.72.0...v1.72.1) (2025-09-26)


### 🐛 Bug Fixes

* handle unprefixed version tags for API/WEB services in external repo ([eb06140](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/eb06140abe12a06b8ec741b23937fc755d0efb8d))
* update API environment variable comment for clarity ([e17f525](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e17f525afdbcf7dcf92192128487a436ecd3552d))

## [1.72.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.71.2...v1.72.0) (2025-09-26)


### 🚀 Features

* add Python script header and import required modules for tag resolver ([c9a6806](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c9a6806b996dde91fe583f7b9f295eb2de15e719))

## [1.71.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.71.1...v1.71.2) (2025-09-26)


### ♻️ Code Refactoring

* enhance tag resolution with service file tracking and improved error handling ([2d1d418](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d1d4185a3801981a19c294c9da6ade05b5757c3))

## [1.71.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.71.0...v1.71.1) (2025-09-26)


### ♻️ Code Refactoring

* simplify tag resolution logic and add external repo support ([2cb9e5d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2cb9e5d96a1547e9fb5d4db69dc42b06ca2e997c))

## [1.71.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.70.0...v1.71.0) (2025-09-26)


### 🚀 Features

* enhance tag resolution with multi-method search and improved error handling ([0468bf9](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/0468bf9c57ee4bf229c86cf668af896270d30de7))


### 🐛 Bug Fixes

* update API service environment variable comment for clarity ([c3c1a6d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c3c1a6d3bad4718ae9d8a915cf39ecf70d8c2dce))


### ♻️ Code Refactoring

* simplify tag resolution by removing storefront-cdk remote tag fetching ([5a5b731](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5a5b73150008c42cc023f01f918924ef795dc187))

## [1.70.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.69.2...v1.70.0) (2025-09-26)


### 🚀 Features

* add GitHub token authentication for git operations in tag resolver ([70e0fa3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/70e0fa353eca0faaf10181f770534640f37dcff3))

## [1.69.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.69.1...v1.69.2) (2025-09-26)


### 🐛 Bug Fixes

* update environment variable comment in API service stack ([6564b2e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6564b2eb3bf1f99d9350db3ae08c882cc7afaae8))


### ♻️ Code Refactoring

* simplify tag resolution logic and improve version parsing for service tags ([47eb877](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/47eb877e72c7c4f3e20af723204162a5e6b66ee5))

## [1.69.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.69.0...v1.69.1) (2025-09-26)


### 🐛 Bug Fixes

* improve tag resolution and require semantic-release success for tag generation ([4d1a6e4](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4d1a6e42d390fc4ad8981d987360d7c30e9a9e95))

## [1.69.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.68.0...v1.69.0) (2025-09-26)


### 🚀 Features

* add semantic-release dependency and fetch API/WEB tags from storefront-cdk repo ([c6b1c32](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c6b1c3290e30df02dca5c106d4ab4c08f3cc0ec8))

## [1.68.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.67.0...v1.68.0) (2025-09-26)


### 🚀 Features

* fetch API/WEB tags from storefront-cdk repo instead of local git history ([f61cb32](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f61cb32ff40da534c6eeb18b188493ce66c58df9))

## [1.67.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.66.2...v1.67.0) (2025-09-26)


### 🚀 Features

* add debug logging for repository dispatch event and payload tags ([2a4f35e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2a4f35e09c8473d88485e4d015d16b94469d79dd))

## [1.66.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.66.1...v1.66.2) (2025-09-26)


### ♻️ Code Refactoring

* simplify tag generation logic and add repository dispatch support ([230cec7](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/230cec7c9bceba695e4e104a2d5da1e2df224155))

## [1.66.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.66.0...v1.66.1) (2025-09-26)


### 🐛 Bug Fixes

* remove environment suffix from stack names and improve tag handling in workflows ([a546c30](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a546c3001e86216267a32f92eaeccc7e3a728db6))
* use existing API/WEB tags from repository dispatch payload instead of incrementing ([b7d0e4f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7d0e4f6c2341a57140a1efe4a3e4a0babd00bd1))

## [1.66.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.66.0...v1.66.1) (2025-09-26)


### 🐛 Bug Fixes

* use existing API/WEB tags from repository dispatch payload instead of incrementing ([b7d0e4f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b7d0e4f6c2341a57140a1efe4a3e4a0babd00bd1))

## [1.66.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.65.0...v1.66.0) (2025-09-26)


### 🚀 Features

* add NetworkStack and MultiAlbStack to critical stack monitoring in CI/CD pipeline ([500e44b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/500e44b61d8b81cf97ca7b67dec9b40ccac52d4b))

## [1.65.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.64.1...v1.65.0) (2025-09-25)


### 🚀 Features

* support environment input param and repository dispatch triggers for service tags ([772d24a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/772d24ab18752cfefdd99d5d7d62a8497a956c92))

## [1.64.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.64.0...v1.64.1) (2025-09-25)


### 🐛 Bug Fixes

* remove conditional skipping of listener and dns worker tags in deployment workflow ([53cd7f7](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/53cd7f778dfbfd2f690f1a5ac5990516a0ee2c97))

## [1.64.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.63.0...v1.64.0) (2025-09-25)


### 🚀 Features

* add database credentials to DNS worker service environment variables ([4753cab](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4753cabe154c9c3554a9fad992ec2dec768ad2c6))

## [1.63.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.62.2...v1.63.0) (2025-09-25)


### 🚀 Features

* track and build listener/dns-worker images independently based on file changes ([5301113](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/53011134bba5d8bc6c954d676de40aeb8d1255aa))

## [1.62.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.62.1...v1.62.2) (2025-09-25)


### ♻️ Code Refactoring

* reorganize apps directory structure and update build workflows for dns-worker and listener services ([5e3f4d7](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5e3f4d72731575b387caf6ef932db2dd46f3b2f1))

## [1.62.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.62.0...v1.62.1) (2025-09-25)


### ♻️ Code Refactoring

* remove debug logging from tag resolver and simplify git tag search ([188a6f4](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/188a6f45eae810e5d7d219f934ba7b721ce10f7d))

## [1.62.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.61.1...v1.62.0) (2025-09-25)


### 🚀 Features

* add debug logging for git tag resolution process ([074b23c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/074b23c68ad60a32e3f77562bb39a76dfada8077))
* add tag_resolver.py to image-related files and update fallback tag logic ([4f83c33](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4f83c331dfc055edc0f3fc63a6a16f3d1527b9d5))

## [1.61.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.61.0...v1.61.1) (2025-09-25)


### ♻️ Code Refactoring

* simplify tag generation by removing auto-increment and improving tag resolution logic ([6c171d0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6c171d093ea0bef46324be568ac243af7bc63492))

## [1.61.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.60.0...v1.61.0) (2025-09-25)


### 🚀 Features

* implement automated service tag increments and improve CI workflow reliability ([f4df959](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f4df9595a055bd915ba1db66c862aa846a19f6a5))


### 🐛 Bug Fixes

* narrow image build trigger to only relevant script files ([ed68f26](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ed68f26cd89c1408db0eecf4b31b631ddb45d90f))

## [1.60.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.60.0...v1.60.1) (2025-09-25)


### 🐛 Bug Fixes

* narrow image build trigger to only relevant script files ([ed68f26](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ed68f26cd89c1408db0eecf4b31b631ddb45d90f))

## [1.60.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.59.4...v1.60.0) (2025-09-25)


### 🚀 Features

* implement simplified tag resolver with clear priority order ([2ab2df8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2ab2df888840c0736d8676aa9d0d4482b74a01c9))


### ♻️ Code Refactoring

* reorder GitHub workflow jobs and update job dependencies for semantic versioning ([7063bba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7063bba13b073bacc292540498ee802191901f7d))
* simplify tag resolver with cleaner priority-based logic ([2265d7b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2265d7b3c3349e7b4902bce120aba5168442cc4b))

## [1.60.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.60.0...v1.60.1) (2025-09-25)


### ♻️ Code Refactoring

* reorder GitHub workflow jobs and update job dependencies for semantic versioning ([7063bba](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7063bba13b073bacc292540498ee802191901f7d))

## [1.60.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.59.4...v1.60.0) (2025-09-25)


### 🚀 Features

* implement simplified tag resolver with clear priority order ([2ab2df8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2ab2df888840c0736d8676aa9d0d4482b74a01c9))

## [1.60.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.59.4...v1.60.0) (2025-09-25)


### 🚀 Features

* implement simplified tag resolver with clear priority order ([2ab2df8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2ab2df888840c0736d8676aa9d0d4482b74a01c9))

## [1.59.4](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.59.3...v1.59.4) (2025-09-25)


### 🐛 Bug Fixes

* add fallback methods for git tag resolution when --sort is unsupported ([48e2d32](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/48e2d327ba2dcea9afc133b4f54a1f2dec48290e))

## [1.59.3](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.59.2...v1.59.3) (2025-09-25)


### ♻️ Code Refactoring

* remove tag_resolver.py from CI build triggers and update comments ([b467990](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b467990aac5cd3385399e2a8000a9efdc09623f9))

## [1.59.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.59.1...v1.59.2) (2025-09-25)


### ♻️ Code Refactoring

* improve tag resolution logic and messaging for skipped service builds ([213aaa4](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/213aaa4b7a138653fec2878e33ec6ec1cb7b4bf2))

## [1.59.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.59.0...v1.59.1) (2025-09-25)


### ♻️ Code Refactoring

* simplify service tag lookup logic with cleaner tag filtering ([e519e18](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e519e1889d92c9e9e65b3486261c5250050b8135))

## [1.59.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.58.1...v1.59.0) (2025-09-25)


### 🚀 Features

* add 042322.xyz and 042325.xyz domains to allowlist ([7eea0b7](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7eea0b7431a0a8616b12d6dad5eb6ea02e2c6b6c))

## [1.58.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.58.0...v1.58.1) (2025-09-25)


### ♻️ Code Refactoring

* implement batch domain processing with database integration in DNS worker ([8bc14f9](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8bc14f95a92fe35665ea9d091c15a1f4126e6721))

## [1.58.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.57.0...v1.58.0) (2025-09-24)


### 🚀 Features

* add concurrency control and stack status checks to infrastructure deployment workflow ([ea61fb9](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ea61fb9b44936cd384c8095b06d67155b3237513))

## [1.57.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.56.1...v1.57.0) (2025-09-24)


### 🚀 Features

* skip version increment when service build is skipped even if files changed ([4c7ea41](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4c7ea411ad7268f399e2aee538da532e1a34e130))

## [1.56.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.56.0...v1.56.1) (2025-09-24)


### 📚 Documentation

* clarify comment about long polling efficiency in DNS worker ([356e7b0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/356e7b0b486b299710aa0d2685bd9f1c8664146d))

## [1.56.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.55.0...v1.56.0) (2025-09-24)


### 🚀 Features

* implement service-specific versioning for container images ([311f6c4](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/311f6c474a61d91b261b4ed932b09b326ceb0598))

## [1.55.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.54.0...v1.55.0) (2025-09-24)


### 🚀 Features

* update DNS worker to use IAM role instead of explicit AWS credentials ([69dbd1e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/69dbd1e43074bcc74ff452df5ede6e83cafa70f2))

## [1.54.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.53.1...v1.54.0) (2025-09-24)


### 🚀 Features

* implement service-specific versioning with automatic version increments ([d154e69](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d154e694fbc2fe64de2285e396d3bd6bbc0fc500))

## [1.53.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.53.0...v1.53.1) (2025-09-24)


### ♻️ Code Refactoring

* improve tag resolution with service-specific file change detection ([55abab8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/55abab8048b86e3f4188925b36596f35937a356f))

## [1.53.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.52.0...v1.53.0) (2025-09-24)


### 🚀 Features

* add DNS worker service with Docker build and deployment workflow ([d54e91e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d54e91e6aa39a7c3ce6e6eff387ee10ef86dc4d3))

## [1.52.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.51.1...v1.52.0) (2025-09-24)


### 🚀 Features

* add SQS managed policy to listener service stack ([4c08a44](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4c08a44b923291e79366a74d5d0cb7627ec44737))

## [1.51.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.51.0...v1.51.1) (2025-09-24)


### 🐛 Bug Fixes

* update environment variable name from SQS_DNS_QUEUE_URL to SQS_DNS_OPERATIONS_QUEUE_URL ([388f389](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/388f38919d5876071dafe39e2918b641e93db3d0))

## [1.51.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.50.2...v1.51.0) (2025-09-24)


### 🚀 Features

* add SQS DNS queue URL environment variable to listener service ([35a22fa](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/35a22fa291e8e5fa6f5dd81641f1c75eef39ff87))

## [1.50.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.50.1...v1.50.2) (2025-09-24)


### 🐛 Bug Fixes

* set ECS deployment circuit breaker via CloudFormation override instead of service config ([80b9f64](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/80b9f64852da66251509b6880c9f32f92b3a20eb))

## [1.50.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.50.0...v1.50.1) (2025-09-24)


### 🐛 Bug Fixes

* update deprecated ECS deployment configuration classes to use CfnService properties ([88f5923](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/88f5923fc800180d86db90f8e1f29c0a0b6ece2e))

## [1.50.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.49.0...v1.50.0) (2025-09-24)


### 🚀 Features

* add deployment circuit breaker and job timeouts to CI/CD workflows ([6ab1a04](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6ab1a0461530e022f437c35e7d139f497b823e9c))

## [1.49.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.48.0...v1.49.0) (2025-09-24)


### 🚀 Features

* migrate DNS operations to SQS-based batch processing system ([90c5389](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/90c5389dbc6cafd8e43c641166bec2cd397040be))

## [1.48.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.47.0...v1.48.0) (2025-09-23)


### 🚀 Features

* add dedicated FIFO dead letter queue for FIFO message handling ([a8e6207](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a8e6207f0b940313ca6a1629ef7ec8252d63b11d))

## [1.47.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.46.1...v1.47.0) (2025-09-23)


### 🚀 Features

* add SQS queues and integrate with API service for message processing ([6f3b403](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6f3b4030168147529030861385b6ddcd74148eda))

## [1.46.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.46.0...v1.46.1) (2025-09-23)


### ♻️ Code Refactoring

* remove OpenSearch endpoint from API and web service stacks ([3a39039](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/3a3903961c85124eef911d18aa0f7fe3f5f84952))

## [1.46.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.45.1...v1.46.0) (2025-09-23)


### 🚀 Features

* add OpenSearch endpoint configuration to API and web services ([a3da3e5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a3da3e52bf07f33ac27ccf720a03243ef9d54264))

## [1.45.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.45.0...v1.45.1) (2025-09-23)


### 🐛 Bug Fixes

* improve git diff detection to handle merge commits correctly ([20b9639](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/20b9639034e242fa0d49014e4a5da188f9c4a8cb))

## [1.45.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.44.0...v1.45.0) (2025-09-23)


### 🚀 Features

* enable OpenSearch role assignment for API and web services ([69a0c71](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/69a0c71009553f7ae69e8c93907f26121b92d289))

## [1.44.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.43.4...v1.44.0) (2025-09-23)


### 🚀 Features

* add manual infrastructure deployment trigger and improve flag display in workflow summary ([e01cea2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e01cea2b6a03ac9e19529deae558d0d08e85fe56))

## [1.43.4](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.43.3...v1.43.4) (2025-09-23)


### ♻️ Code Refactoring

* remove OpenSearch role assignments from API and web services ([4756212](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/475621248b841852c374414ec90745e76eb41316))

## [1.43.3](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.43.2...v1.43.3) (2025-09-23)


### ♻️ Code Refactoring

* remove unused opensearch_role parameter from service stacks ([b16e27c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b16e27c10aa058c3f01499aad17b1ea5bce0a05a))

## [1.43.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.43.1...v1.43.2) (2025-09-23)


### 🐛 Bug Fixes

* use provided OpenSearch task role or create new one for Fargate service ([d32fb3d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d32fb3d525f5377dffd7a4e1ee119e550ea62548))

## [1.43.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.43.0...v1.43.1) (2025-09-23)


### 🐛 Bug Fixes

* set correct task role principal for Fargate service task definition ([d237bc9](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d237bc9856368c501328252766db8113eb124a6e))

## [1.43.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.42.1...v1.43.0) (2025-09-23)


### 🚀 Features

* add skipped status handling in deployment summary report ([312359f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/312359fe1d51b173a73694d33e9bb00b1d384732))

## [1.42.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.42.0...v1.42.1) (2025-09-23)


### 📚 Documentation

* add deployment logs and history links to workflow summary ([e13f481](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e13f481b248a5d86f6f8d2cbfe9f13f4d5841443))

## [1.42.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.41.0...v1.42.0) (2025-09-23)


### 🚀 Features

* add error handling for domains.json file loading with fallback ([9cb13f0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9cb13f08f8f5fee806157670109090fca948753b))

## [1.41.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.40.0...v1.41.0) (2025-09-23)


### 🚀 Features

* add domains config loading from JSON file ([24e36fb](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/24e36fb2d1b8f29924a756ad164f9e46e3c3bdb0))

## [1.40.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.39.2...v1.40.0) (2025-09-23)


### 🚀 Features

* enhance deployment summary with conditional steps and expanded AWS links ([7909cfd](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7909cfd7f373d5a7b26a0aafb7a0c1dd76d63ab0))

## [1.39.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.39.1...v1.39.2) (2025-09-23)


### ♻️ Code Refactoring

* remove domain sync logic from CDK app deployment ([b660d31](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b660d315fe845f7c48a976520dd78fe66efa20e0))

## [1.39.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.39.0...v1.39.1) (2025-09-23)


### 🐛 Bug Fixes

* remove hardcoded domain fallback and exit deployment if domains cannot be determined safely ([dc31237](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/dc3123767a9c4db7faa1e7903ccfccf3eef74276))

## [1.39.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.38.1...v1.39.0) (2025-09-23)


### 🚀 Features

* add domains.json to infrastructure file change detection patterns ([2e9fe7d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2e9fe7dbe871f57f35ba0da7e196617bd9f34f22))

## [1.38.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.38.0...v1.38.1) (2025-09-23)


### 📚 Documentation

* remove outdated comment about LISTEN persistence in setup_listener ([42f8926](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/42f892694ef7fe675ddc923bd426772f0d4f8b60))

## [1.38.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.37.0...v1.38.0) (2025-09-23)


### 🚀 Features

* add clean restore option to Kubegres-to-RDS backup script and reorder workflow inputs ([2f796bb](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2f796bb8cd54adc2d51778c0f11b4c3f907b52ac))
* add repository_dispatch trigger for infrastructure deployment workflow ([7de174e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/7de174e187f9475f1dfc6c5cff3687ad198af930))


### 🐛 Bug Fixes

* update PostgreSQL LISTEN channel name to domain_status_changed ([d5d18e4](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d5d18e4921f9f7013339591c991e126f81d90660))


### ♻️ Code Refactoring

* simplify image tag handling in CDK deployment workflow ([faa73d4](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/faa73d46ae7aecf85d2d0b43adb1453a865ba6ed))

## [1.37.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.36.0...v1.37.0) (2025-09-22)


### 🚀 Features

* enhance domain fallback and image tag resolution with git-aware defaults ([2ba1a80](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2ba1a806360db10f0bfa8cfe3d7d430cd22097eb))

## [1.36.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.35.2...v1.36.0) (2025-09-22)


### 🚀 Features

* add AWS_REGION environment variable to API and web service stacks ([5d9a3be](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5d9a3be063d6894a4a386bba784cd1fd1372f536))

## [1.35.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.35.1...v1.35.2) (2025-09-22)


### ♻️ Code Refactoring

* comment out unused ParametersStack initialization ([42c56da](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/42c56da9aae309e4911d5585ebd593257cc10ca8))

## [1.35.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.35.0...v1.35.1) (2025-09-22)


### ♻️ Code Refactoring

* gracefully handle domain update failures with empty fallback list ([2c74bda](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2c74bda3cd6f8b3d003bd9526def8421867edbee))

## [1.35.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.34.0...v1.35.0) (2025-09-22)


### 🚀 Features

* add extensive debug logging for AWS credentials and database connectivity ([55f5aa4](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/55f5aa478dfa5ae48a2d6de0fbf492efeeb30ea3))

## [1.34.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.33.0...v1.34.0) (2025-09-22)


### 🚀 Features

* improve domain update logging and reduce service instance count to 1 ([2d3618f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d3618f362fb4ee385886a7f9eba1bd91b4cd7fe))

## [1.33.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.32.0...v1.33.0) (2025-09-22)


### 🚀 Features

* add custom OpenSearch task role support and direct migration script ([c8c485c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c8c485c84248312c56c4c09bb533dcc0d2dff34e))

## [1.32.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.31.1...v1.32.0) (2025-09-22)


### 🚀 Features

* add OpenSearch service role for S3 snapshot access ([a0784c4](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a0784c42c5fff19f97b776b2facbebdee44bf284))

## [1.31.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.31.0...v1.31.1) (2025-09-22)


### 🐛 Bug Fixes

* remove build-listener dependency from deploy-infrastructure ([094ae41](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/094ae412fae33c6d966d3cf91350af15ababa044))

## [1.31.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.30.1...v1.31.0) (2025-09-22)


### 🚀 Features

* add OpenSearch stack with public domain and migration scripts ([0a3c3ad](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/0a3c3adca81e0d3725e864129258d99d3157da65))

## [1.30.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.30.0...v1.30.1) (2025-09-18)


### ♻️ Code Refactoring

* improve change detection logic and add detailed GitHub Actions summary ([30b1d74](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/30b1d7495f5fe507cb7cf9666d681522939f3930))

## [1.30.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.29.0...v1.30.0) (2025-09-18)


### 🚀 Features

* add change detection summary to GitHub workflow output ([9ceb9ac](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/9ceb9ac24758d90072ec9abf60cdcf81f26ece5a))

## [1.29.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.28.0...v1.29.0) (2025-09-18)


### 🚀 Features

* add debug logging to GitHub workflow change detection script ([e48674d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e48674d7a6f2bc99b03c3d3d13490ce3503f240b))

## [1.28.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.27.2...v1.28.0) (2025-09-18)


### 🚀 Features

* add image_tag input parameter to infrastructure build workflow ([65d2790](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/65d279053b72b23686a870acf001631297e3279b))


### ♻️ Code Refactoring

* update GitHub Actions workflows with separate image tags and improved deployment summaries ([8a87c5c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8a87c5cd201afa34202d6141edf9e81f9d90a8a4))

## [1.27.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.27.1...v1.27.2) (2025-09-18)


### ♻️ Code Refactoring

* update domain activation to sync all active domains instead of single domain ([e6859a4](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e6859a4ff15801e022a4282c3ca32e9ce43d3374))

## [1.27.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.27.0...v1.27.1) (2025-09-17)


### ♻️ Code Refactoring

* simplify workflow triggers by removing repository_dispatch events ([4b3bee8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4b3bee8b0a26de030ac7a19000622ff216f31db5))

## [1.27.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.26.0...v1.27.0) (2025-09-17)


### 🚀 Features

* add cloud map DNS registration for listener service and disable force builds ([27ca401](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/27ca401188bf312b01126a8c9d21c337fdc165e4))
* add CloudMap DNS registration and auto-trigger infrastructure workflow on code changes ([e00c4da](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e00c4da3495a649982d6111f3f9cec43c33b4fb7))
* add comprehensive logging to listener service for debugging ([6c2c9f7](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6c2c9f7aead6d2aebc2a99c95eb0bd6f96dd85c3))
* add database connection monitoring and auto-reconnect to domain listener ([55c388d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/55c388de8a65dd7079399f19ef0f76caa5f95928))
* add dynamic image tag generation for listener builds based on branch/SHA ([a4b5d67](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a4b5d679e8db444358f9fa347217f45f835d242e))
* add periodic domain check as fallback to notification-based updates ([f4ef5ab](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f4ef5abe24c0a9b531072b1205c659d09b675da3))
* add Route53 permissions to Fargate task role for hosted zone operations ([0e4d2e5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/0e4d2e5e9c351856158a0ba50de2ab2ab825599c))
* add special image tag handling for domain-update branches and skip prod deployment ([c4a6f60](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c4a6f6019b9d825b5be7df7c0a7420851eb59aae))
* add support for Secrets Manager secrets in FargateServiceConstruct ([8aaa37e](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/8aaa37ebf34e01423841ad636fe59ef43c159204))
* add workflow dispatch inputs for environment selection and deployment options ([0d861bf](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/0d861bfb4bd9f76175a306872b8252e7b6230404))
* add workflow_call inputs and secrets to infra-build workflow ([aeaaaaf](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/aeaaaaf309f764611899ba22b00a07a788ee644d))
* auto-trigger image builds and infra deployments for domain update branches ([aeec6a7](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/aeec6a7221df8675ed2a8c50e8e568b05120babf))
* auto-trigger infrastructure deployment when images are built successfully ([1406f2a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1406f2a2e9db8f2600e3aa3bb98db3526115c911))
* create timestamped branch for domain updates instead of direct main commits ([e7d97b1](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e7d97b16f6e97bdae59a41d11ebcf21f043d2e71))
* expose image tag output from build workflow and use in semantic release ([b9c504f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b9c504f66849f5adac506ab8e65f4743975d7d8c))
* expose semantic release outputs for downstream workflows ([fe4104c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/fe4104c03cad12ec773b761713d5174ae967589b))
* implement git branch-based domain updates instead of workflow dispatch ([5a92640](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5a9264042c35a7d7c215134c8c9d0f1a2dce2504))
* implement separate image tags for listener, API and web services ([986758d](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/986758d52b111f05af97ac96a94468f237bcc822))
* improve image tag handling and add domain-updates branch support ([5c03087](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5c03087d224b0ef197ab81015b1460eaac51d59d))
* parse JSON notifications and handle active/inactive domain status changes ([52adf48](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/52adf4874033663088f0f5d40be37a5afb4dd7ac))
* pass LISTENER_IMAGE_TAG as CDK_IMAGE_TAG env var during deployment ([2081743](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2081743b522ffa50ae45da92b372e66bc9d8cca0))


### 🐛 Bug Fixes

* add cursor cleanup, connection health checks, and error handling in domain listener ([ed43988](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ed43988a62f91414f7615c2d6e72be2336050f17))
* add delay after creating hosted zones to allow DNS propagation ([0b8a26a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/0b8a26a7d2b3c3079bc098740ec2e4dab2491d8d))
* add quotes around boolean values and debug output in build check step ([d389a04](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d389a04b555e579074c1b5038811df5ed17f9678))
* improve database listener reliability with autocommit and simplified connection handling ([72d4adb](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/72d4adb8f071f1a9ec9c99db9bfbe515993e8a4b))
* increase domain check interval to daily and remove redundant continue statement ([6819798](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/68197989421f2b8526831b25f192b5d9ecf60c75))
* only trigger infrastructure deploy when image changes build successfully ([6f5aa91](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/6f5aa91683c6cba0946530d5cf34a5d76bd173ce))
* simplify domain logging output by removing full URL extraction ([ec43b2f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/ec43b2f9eef827fe8c91abd3ed3c6844d2822e87))
* skip tag generation on main branch and improve log message timing ([a87b3ea](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a87b3eae68f800203f1e09374db66de87ceb01ce))
* syntax errors and file path in infra deployment workflow ([aca0c6c](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/aca0c6caeb5c4304e6562da70e35501c389bf05c))
* update deployment summary job dependencies from dev-deployment to deploy-infrastructure ([97c43bb](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/97c43bb44c68fbfb266279835b5c82b4cba1ad57))
* update domain-update branch name pattern to domain-updates ([055b9c2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/055b9c29294035d1ccc1203fbc2cdb9e4abcd46c))
* update image tag fallback logic in infra workflow to use generated tag ([f68fec2](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f68fec24233bb0d3790853d1ae7158fb4cd742e2))
* update workflow dependencies and tag reference in listener build pipeline ([65b2f73](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/65b2f731ed9cf00b19cf33d1be49ced0bbdb3e74))
* use latest tag when no image changes or build fails in semantic release workflow ([676dfbe](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/676dfbe244d023f35cacabd6a065d4a7ef3bf99f))


### ♻️ Code Refactoring

* extract image building logic into reusable workflow with change detection ([bf081bc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/bf081bc4c5fd5cd000a62cdab3cf3bfc0b741c55))
* improve CI/CD workflows with better error handling and environment support ([e1780de](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e1780de07e292bd0740d067075f3231159e4859e))
* remove periodic domain check in favor of notification-only updates ([0a0d9cc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/0a0d9cccd34423e7715729d52b48aa3b938746f9))
* remove redundant comment about 60 second timeout in listener loop ([af01320](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/af01320e1ec269401cbd9fad48db52864f7cf8c1))
* remove redundant comment about periodic check in listener loop ([f2a9a52](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f2a9a52f468abb28bb2282d23ced52f0976d732c))
* remove semantic-release dependency and simplify Fargate service configuration ([4c69a38](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/4c69a38a921c3eac60b689c9b282ca154f2405e1))
* rename build-and-push-listener job and fix domain update detection logic ([c7b8a6b](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c7b8a6bb411b294ee0ca84914d4b942bb205b1dc))
* rename build-images workflow to listener-build and standardize workflow naming ([c327ecc](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c327ecc2e5474e9c5ba2e6009bc6f50dcd8930c2))
* replace FargateServiceConstruct with direct ECS task and service definitions ([b4839d1](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b4839d13c2e99d38d0d72f90bb4c8a63967c86bf))
* simplify GitHub integration by committing directly to main branch instead of creating PRs ([a508d19](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a508d19379847a01636ac586f3f0d8932ae1d280))
* simplify GitHub workflow trigger to use fixed branch for domain updates ([efa8214](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/efa8214cf767367a836d8ba7e0dde0acf348dce7))
* simplify image tag handling to use separate environment variables per service ([e41789f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e41789f30d5f222aaf2fb1ab089a3823ea303b77))
* simplify listener loop error handling and remove redundant reconnection logic ([a13e1a1](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a13e1a1225eef9b6361251cddab9eec20d8afce7))
* split build and deploy workflows to run conditionally based on change type ([cf0e665](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/cf0e66550658e2602701e41417945169b9c23152))
* split monolithic workflow into separate build files for infra and listener ([fbb0be4](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/fbb0be412072d9a3d19cc195a927da600659a2f1))
* streamline CI/CD pipeline with cleaner job organization and improved comments ([b143c55](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b143c553e97a1c5b2a8ede1c05faf8ca1072c2ce))
* streamline deployment workflow and remove verbose logging ([355a88a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/355a88a91a29328b384d9dbd322245ac3130f04a))

## [1.26.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.25.0...v1.26.0) (2025-09-16)


### 🚀 Features

* add ListenerServiceStack import to app entrypoint ([5379b3a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/5379b3a400d5bfdfb47e643f7834620117cd4b61))


### 📚 Documentation

* add clarifying comments for stack definitions in app.py ([a99b7b3](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/a99b7b3aefdfa0d7df08d9082ac1b34c5c2e6a69))


### ♻️ Code Refactoring

* remove redundant stack comments in app.py ([94fcd96](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/94fcd96f0369d2754ec919d59be919af8d51d2d3))
* replace AWS Secrets Manager with environment variables for database credentials ([2b647e8](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2b647e8ba71d85a36b572bd62307ff56feaf6e65))

## [1.25.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.24.0...v1.25.0) (2025-09-16)


### 🚀 Features

* add listener service deployment with GitHub token integration ([c6650c5](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/c6650c5d2122842d29455bef1068aec5082db836))

## [1.24.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.23.1...v1.24.0) (2025-09-16)


### 🚀 Features

* auto-create Route53 hosted zones and update CDK stacks to use zone lookups ([43ca503](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/43ca503a0d92e56184885bb3b1f5b3c04345d925))

## [1.23.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.23.0...v1.23.1) (2025-09-16)


### ♻️ Code Refactoring

* replace Route53 zone lookups with direct zone creation for better CDK handling ([b6969e4](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/b6969e42cf417bae6d73af7c3c65757f907a5d18))

## [1.23.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.22.1...v1.23.0) (2025-09-15)


### 🚀 Features

* add domains input param and JSON file generation to GitHub workflow ([1531793](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/15317937e4b05d7a9f603f6d2e4d53caa55ad881))

## [1.22.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.22.0...v1.22.1) (2025-09-15)


### ♻️ Code Refactoring

* remove domain updater service and consolidate domain update logic into listener ([911ccf0](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/911ccf0c258d6656d0e9b4064c1e25c863132a6d))

## [1.22.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.21.2...v1.22.0) (2025-09-15)


### 🚀 Features

* add service_name parameter to DomainUpdaterStack constructor ([0c6f0eb](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/0c6f0eb24ece27164d674ab5254feee4a1edef4f))

## [1.21.2](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.21.1...v1.21.2) (2025-09-15)


### 🐛 Bug Fixes

* use secure string parameter for GitHub token and move DB secret to environment vars ([d3f148a](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/d3f148a33fcbbfe22d6ba8c3b4de3d53247a1b70))

## [1.21.1](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.21.0...v1.21.1) (2025-09-15)


### 🐛 Bug Fixes

* update DB secret access to use SecretsManager and improve ECR repository error handling ([2d59366](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/2d59366e7840603fe85dd59cc7892e4c03a7ae44))

## [1.21.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.20.0...v1.21.0) (2025-09-15)


### 🚀 Features

* add domain updater service with GitHub integration for automated domain management ([1a94192](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/1a94192b0086a9bb000bc5f383d2cbedc65ec42e))

## [1.20.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.19.0...v1.20.0) (2025-09-15)


### 🚀 Features

* add domain listener service with GitHub Actions workflow integration ([36a89f7](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/36a89f7c6255f65e88ef7f2b76535f39b1a409f2))

## [1.19.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.18.0...v1.19.0) (2025-09-15)


### 🚀 Features

* add dedicated security group for ALB with restricted inbound rules ([f3ab30f](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/f3ab30f7f41404ca0b81ddbfae8b7dd8d4732a0c))

## [1.18.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.17.0...v1.18.0) (2025-09-15)


### 🚀 Features

* allow ECS task-to-task communication via security group ingress rule ([fd3e795](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/fd3e79529cb90e6e45f9a4771eb50b51547f66d3))

## [1.17.0](https://github.com/AITeeToolkit/aws-fargate-cdk/compare/v1.16.0...v1.17.0) (2025-09-15)


### 🚀 Features

* dynamically detect and remove semantic version tags and scale web service to 2 containers ([e42d009](https://github.com/AITeeToolkit/aws-fargate-cdk/commit/e42d009c3e4d05f4fb62f972dd631c13fffbb90b))

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
