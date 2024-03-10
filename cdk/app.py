from aws_cdk import (
    App,
    Stack,
    aws_iam as iam,
    aws_ec2 as ec2,
    CfnOutput
)
from constructs import Construct

class DiscordBotEC2Stack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # VPCの作成
        vpc = ec2.Vpc(self, "VPC", max_azs=2)

        # IAMロールの作成
        ec2_role = iam.Role(
            self, "EC2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )

        # EC2セキュリティグループの定義
        ec2_sg = ec2.SecurityGroup(
            self, "DiscordBedrock-EC2-Sg",
            vpc=vpc,
            allow_all_outbound=True,
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
        ec2_instance = ec2.Instance(
            self, "EC2Instance",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.GenericLinuxImage({'ap-northeast-1': 'ami-012261b9035f8f938'}),
            vpc=vpc,
            role=ec2_role,
            security_group=ec2_sg,
            user_data=user_data, 
            ssm_session_permissions=True  # SSMセッションマネージャのアクセスを許可
        )

        # SSMセッション開始コマンドの出力
        CfnOutput(
            self,
            "StartSsmSessionCommand",
            value=f"aws ssm start-session --target {ec2_instance.instance_id}\n\n"
                "sudo su - ec2-user",
            description="上記のコマンドを実行してSSMを利用してEC2に接続してください",
        )

        # 第3回目に必要　Bedrockモデル呼び出し権限のインラインポリシーを作成しロールにアタッチ
        ec2_role.add_to_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=["*"],
            effect=iam.Effect.ALLOW
        ))

        # 第4回目に必要　翻訳権限のインラインポリシーを作成しロールにアタッチ
        ec2_role.add_to_policy(iam.PolicyStatement(
            actions=["translate:TranslateText"],
            resources=["*"],
            effect=iam.Effect.ALLOW
        ))

        # 第5回目に必要　S3のインラインポリシーを作成しロールにアタッチ
        ec2_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:*"],
            resources=["arn:aws:s3:::*"],
            effect=iam.Effect.ALLOW,
        ))

        # 第5回目に必要　Secrets Manager アクセス権限のインラインポリシーを作成しロールにアタッチ
        ec2_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
            ],
            resources=["*"],
            effect=iam.Effect.ALLOW,
        ))

app = App()
DiscordBotEC2Stack(app, "DiscordBotEC2Stack")
app.synth()
