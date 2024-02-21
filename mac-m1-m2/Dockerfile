# Python 3.9のベースイメージを使用
FROM python:3.9

# 作業ディレクトリを設定
WORKDIR /work

# aws cliのインストール
RUN apt-get update && \
    apt-get install -y awscli

# Node.jsのインストール
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs
RUN npm install -g npm@latest

# AWS CDKのグローバルインストール
RUN npm install -g aws-cdk

# SSM Pluginのインストール
RUN curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_arm64/session-manager-plugin.deb" -o "session-manager-plugin.deb" && \
    dpkg -i session-manager-plugin.deb && \
    rm session-manager-plugin.deb
    
# AWS認証ファイル格納ディレクトリを作成
RUN mkdir ~/.aws

# 依存関係をコピー
COPY requirements.txt .

# 依存関係をインストール
RUN pip install -r requirements.txt

# AWSのデフォルトリージョンを設定
ENV AWS_DEFAULT_REGION=ap-northeast-1  

# タイムゾーンを日本時間に設定
ENV TZ=Asia/Tokyo

# コンソールの表示を変えてわかりやすく
RUN echo "alias ls='ls --color=auto'" >> /root/.bashrc && \
    echo "PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@cdk-container\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '" >> /root/.bashrc

ENTRYPOINT ["/bin/bash"]