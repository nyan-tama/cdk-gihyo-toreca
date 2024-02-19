## Dockerイメージの作成
```
docker build -t cdk-gihyo-toreca .
```
## Dockerの起動とDockerの中に入る
```
docker run --rm -it -v ~/.aws:/root/.aws -v ${PWD}:/root/work cdk-gihyo-toreca
```
## python環境の準備
```
pip3 install -r requirements.txt
```
## AWS本番環境の初期設定
```
# 実行は初回時のみでOK CDKデプロイに必要な設定AWSに上に作成される
# すでに作成済みの場合不要
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

#実行したい各チャプターを指定
cd chapter-1

#READMEのマニュアルを参照
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