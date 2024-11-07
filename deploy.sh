#!/bin/bash

# Carregar variáveis do arquivo .env
set -o allexport
source .env
set +o allexport

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Opções do rsync
RSYNC_OPTIONS="-avzh --delete --exclude-from=./.rsyncignore"

# Comando rsync
echo "Iniciando deploy com rsync..."
rsync $RSYNC_OPTIONS -e "ssh -i $SSH_KEY_PATH" . $SERVER_USER@$SERVER_IP:$DEST_DIR

# Enviar o arquivo settings.prod.json para o servidor
rsync -avzh -e "ssh -i $SSH_KEY_PATH" ./config/settings.prod.json $SERVER_USER@$SERVER_IP:$DEST_DIR/config/settings.json

# Criar ou atualizar o arquivo .env no servidor
ssh -i $SSH_KEY_PATH $SERVER_USER@$SERVER_IP "echo 'ENV=production' > $DEST_DIR/.env"

# Instalar python3-venv se não estiver instalado e criar o ambiente virtual
ssh -i $SSH_KEY_PATH $SERVER_USER@$SERVER_IP "cd $DEST_DIR && \
if ! dpkg -l | grep -q python3-venv; then \
    sudo apt update && sudo apt install -y python3-venv; \
fi && \
if [ ! -d venv ]; then \
    python3 -m venv venv; \
fi && \
cd $DEST_DIR; ./venv/bin/pip install -r requirements.txt"

# Final message
echo "Deploy concluído com sucesso!"
