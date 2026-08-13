# ☁️ Guia de Publicação Online: Supabase & Streamlit Cloud

Este guia foi elaborado para você publicar o **CXPack Radar** online na nuvem gratuitamente, garantindo que toda a sua equipe (Sérgio, João, Maria, etc.) consiga acessar a plataforma com segurança.

---

## 1. Criar o Banco de Dados Online no Supabase (PostgreSQL Gratuito)

1. Acesse o site do Supabase: 👉 **[https://supabase.com](https://supabase.com)**
2. Clique em **"Sign Up"** e faça login com sua conta do GitHub ou Google.
3. Clique em **"New Project"** (Novo Projeto).
4. Preencha os campos:
   - **Name**: `cxpack-radar-db`
   - **Database Password**: Crie uma senha forte e anote-a.
   - **Region**: Escolha `South America (São Paulo)` se disponível, ou `East US`.
   - **Pricing Plan**: Selecione `Free Tier` (Gratuito).
5. Clique em **"Create new project"** e aguarde cerca de 2 minutos até o banco ser provisionado.
6. Após a criação, no menu lateral esquerdo, vá em **Project Settings** -> **Database**.
7. Na seção **Connection String**, selecione a aba **URI**.
8. Copie o endereço exibido. Ele terá o seguinte formato:
   `postgresql://postgres:[SUA_SENHA]@db.xyz.supabase.co:5432/postgres`
   *(Substitua `[SUA_SENHA]` pela senha que você criou no passo 4).*

---

## 2. Enviar o Código do Projeto para o GitHub

1. Acesse **[https://github.com](https://github.com)** e crie um novo repositório privado chamado `cxpack-radar`.
2. No seu computador, abra o terminal na pasta do projeto e execute os comandos:

```bash
git init
git add .
git commit -m "Inicializando CXPack Radar"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/cxpack-radar.git
git push -u origin main
```

*(O arquivo `.gitignore` criado pelo sistema garante que suas chaves secretas locais e o banco SQLite não sejam enviados para a internet).*

---

## 3. Publicar no Streamlit Community Cloud

1. Acesse o site do Streamlit Cloud: 👉 **[https://streamlit.io/cloud](https://streamlit.io/cloud)**
2. Clique em **"Sign in"** e conecte sua conta do GitHub.
3. Clique no botão azul **"Create app"** -> **"Yup, I have an app"**.
4. Preencha os campos de deploy:
   - **Repository**: `SEU_USUARIO/cxpack-radar`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
5. Antes de clicar em Deploy, abra a seção **Advanced settings...** (ou clique nos três pontinhos em **Secrets**).

---

## 4. Configurar os Segredos (Secrets) na Nuvem

Na caixa de texto dos **Secrets**, cole a sua API Key do Gemini e a URL do PostgreSQL do Supabase:

```toml
# Chave da API do Google Gemini
GEMINI_API_KEY = "AIzaSyD..."

# Conexão com o PostgreSQL do Supabase (O código usará este banco automaticamente)
DATABASE_URL = "postgresql://postgres:SuaSenha@db.xyz.supabase.co:5432/postgres"
```

Clique em **Save** (Salvar) e em seguida em **Deploy!**.

---

## 5. Tornar o App Privado e Convidar a Equipe

Para garantir que apenas pessoas autorizadas acessem seu sistema:

1. No painel do aplicativo no Streamlit Cloud, vá nas configurações do app (**App Settings** -> **Sharing**).
2. Marque a opção **"Make this app private"** (Tornar este app privado).
3. Na caixa de e-mails de convite, adicione os e-mails autorizados da sua equipe (exemplo: `sergio@empresa.com.br`, `joao@empresa.com.br`, `maria@empresa.com.br`).
4. Clique em **"Save"**. Cada membro receberá um e-mail do Streamlit autorizando o acesso!
