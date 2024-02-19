from aws_cdk import (
    App,
    Stack,
    Duration,
    RemovalPolicy,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_s3_notifications as s3_notifications,
    aws_ec2 as ec2,
    CfnOutput,
)
from constructs import Construct
import json

class DiscordBedrockStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # IAMロールの作成
        ec2_role = iam.Role(
            self, "DiscordBedrockEC2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )

        # VPCの作成
        vpc = ec2.Vpc(self, 'DiscordBedrockVpc', max_azs=1)

        # EC2セキュリティグループの定義
        ec2_sg = ec2.SecurityGroup(
            self, "DiscordBedrock-EC2-Sg",
            vpc=vpc,
            allow_all_outbound=True,
        )

        # HTTPアクセスを許可
        ec2_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP access from the Internet",
        )

        # HTTPSアクセスを許可
        ec2_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS access from the Internet",
        )

        # EC2インスタンスの定義の前にユーザーデータスクリプトを定義
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "sudo dnf update -y",  # システムの更新
            "sudo dnf install -y git docker",  # GitとDockerのインストール
            "sudo systemctl start docker",  # Dockerサービスの開始
            "sudo systemctl enable docker",  # Dockerサービスの自動起動設定
            "sudo usermod -aG docker ec2-user",  # ec2-userをdockerグループに追加
        )

        # EC2インスタンスの定義
        ec2_instance1 = ec2.Instance(
            self, "DiscordBedrock-EC2",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.GenericLinuxImage({'ap-northeast-1': 'ami-012261b9035f8f938'}),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=ec2_sg,
            user_data=user_data, 
            role=ec2_role,
            ssm_session_permissions=True  # SSMセッションマネージャのアクセスを許可
        )

        # Elastic IPの作成
        eip = ec2.CfnEIP(self, "EIP")

        # EC2インスタンスにElastic IPを関連付ける
        eip_association = ec2.CfnEIPAssociation(
            self,
            "EipAssociation",
            eip=eip.ref,
            instance_id=ec2_instance1.instance_id
        )

        # # Lambdaレイヤーの定義
        # lambda_layer = lambda_.LayerVersion(
        #     self, "MyRequestsLayer",
        #     code=lambda_.Code.from_asset("./lambda-layer.zip"),
        #     compatible_runtimes=[lambda_.Runtime.PYTHON_3_11]
        # )

        # # Create IAM Role for Lambda
        # lambda_role = iam.Role(self, 'DiscordBedrockLambdaRole',
        #     assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
        #     managed_policies=[
        #         iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
        #         iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess')
        #     ]
        # )

        # # Create Lambda Function
        # lambda_function = lambda_.Function(self, 'DiscordBedrockLambdaFunction',
        #     function_name='discord-post-lambda-function',
        #     runtime=lambda_.Runtime.PYTHON_3_9,
        #     code=lambda_.Code.from_asset('lambda'),
        #     handler='discord-post-lambda.handler',
        #     role=lambda_role,
        #     timeout=Duration.seconds(30),
        #     layers=[lambda_layer]
        # )

        # # Create a new S3 Bucket for Uploads
        # image_bucket = s3.Bucket(self, 'DiscordBedrockLambdaImageBucket',
        #     bucket_name='DiscordBedrockLambdaImageBucket',
        #     removal_policy=RemovalPolicy.DESTROY,
        #     auto_delete_objects=True
        # )

        # # Add event notification for Lambda function
        # image_bucket.add_event_notification(s3.EventType.OBJECT_CREATED_PUT,
        #     s3_notifications.LambdaDestination(lambda_function)
        # )

        # SSMセッション開始コマンドの出力
        CfnOutput(
            self,
            "StartSsmSessionCommand",
            value=f"aws ssm start-session --target {ec2_instance1.instance_id}",
            description="上記のコマンドを実行してSSMを利用してEC2に接続してください",
        )

        # Elastic IPアドレスの出力
        CfnOutput(
            self,
            "ElasticIpAddress",
            value=eip.ref,
            description=
            "The Elastic IP address of the EC2 instance",
        )

app = App()
DiscordBedrockStack(app, "DiscordBedrockStack")
app.synth()