# Sistema de Replay de Câmera

Captura contínua dos últimos 30 segundos via Iriun Webcam. Pressione ENTER para salvar o clip e fazer upload automático para o Cloudflare R2.

## Pré-requisitos

- Python 3.10+
- [Iriun Webcam](https://iriun.com/) instalado no computador e no celular (ambos na mesma rede Wi-Fi)
- Conta no [Cloudflare R2](https://developers.cloudflare.com/r2/) com bucket criado

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

1. Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

2. Edite o `.env`:

```env
CAMERA_INDEX=0          # índice da Iriun (0, 1, 2... ou deixe em branco para auto)
BUFFER_SECONDS=30
FPS=30

R2_ACCOUNT_ID=abc123    # encontrado em r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=soccer-replay
R2_PUBLIC_URL=https://pub-xxx.r2.dev   # opcional
```

### Como criar o bucket e gerar credenciais no R2

1. Acesse o [painel do Cloudflare](https://dash.cloudflare.com/) → **R2 Object Storage**
2. Clique em **Create bucket** e escolha um nome (ex: `soccer-replay`)
3. Para tornar o bucket público: vá em **Settings** → **Public access** → ative o domínio `r2.dev`
4. Para gerar as credenciais: **Manage R2 API Tokens** → **Create API Token**
   - Permissões: `Object Read & Write`
   - Copie o **Access Key ID** e o **Secret Access Key** para o `.env`
5. O `R2_ACCOUNT_ID` está na URL do bucket: `https://<account_id>.r2.cloudflarestorage.com`

## Uso

### Modo normal (com upload para R2)

```bash
python main.py
```

Pressione **ENTER** a qualquer momento para salvar e enviar o replay.

### Dry-run (apenas salva localmente, sem upload)

```bash
python main.py --dry-run
```

### Especificar pasta de saída

```bash
python main.py --dry-run --output-dir ./output
```

Pressione **Ctrl+C** para encerrar.

## Estrutura

```
soccer-replay/
├── main.py        # loop principal
├── buffer.py      # buffer circular de frames em RAM
├── recorder.py    # gera o arquivo .mp4
├── uploader.py    # upload para Cloudflare R2
├── config.py      # carrega variáveis do .env
├── .env           # credenciais (não commitar)
├── .env.example   # modelo
└── requirements.txt
```
