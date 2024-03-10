## Dockerの起動とDockerの中に入る
```
docker-compose run --rm cdk
```
コンテナから出る時は『exit』を入力して下さい。
```
exit
```

## CDK環境の初期設定
```
# 実行は初回時のみでOK CDKデプロイに必要な設定がAWSに上に作成される
# すでに作成済みの場合は実行不要
cdk bootstrap 
```
## AWS本番環境の構築 
```
cdk deploy
```
## EC2への接続 AWSのSSM接続を利用
```
aws ssm start-session --target EC2のインスタンスID
sudo su - ec2-user
```
## githubからコードを読み込む
```
git clone https://github.com/あなたのgithubアカウント名/gihyo-toreca.git
cd gihyo-toreca

# 実行したい各チャプターを指定
cd chapter-2など

# READMEのマニュアルを参照
cat README.md
```

## EC2の接続解除
```
exit
```

## AWS本番環境の削除
```
cdk destroy
```

## Dockerの終了
```
exit
```