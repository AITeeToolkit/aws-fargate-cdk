from aws_cdk import Stack, aws_ecs as ecs, aws_ec2 as ec2, aws_elasticloadbalancingv2 as elbv2
from constructs import Construct
from cdk_constructs.fargate_service_construct import FargateServiceConstruct

class WebServiceStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        cluster: ecs.ICluster,
        listener: elbv2.ApplicationListener,
        image_uri: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Public-facing web service routed via ALB
        fargate_construct = FargateServiceConstruct(
            self, "WebService",
            cluster=cluster,
            vpc=vpc,
            container_image=ecs.ContainerImage.from_registry(image_uri),
            listener=listener,
            path_pattern="/*",
            priority=200,
            container_port=3000,
            environment={
                "ENV": "production"
            }
        )

        # Expose the service from this stack
        self.service = fargate_construct.service