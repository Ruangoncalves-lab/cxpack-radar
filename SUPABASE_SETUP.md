# Guia de Configuração do Banco de Dados no Supabase (PostgreSQL)

Este guia orienta o passo a passo simples para conectar o **CXPack Radar** a um banco de dados PostgreSQL gratuito no **Supabase**.

---

## 🛠️ Passo a Passo Simples

### 1. Criar uma Conta no Supabase
Acesse **[https://supabase.com](https://supabase.com)** e crie uma conta gratuita.

### 2. Criar um Novo Projeto
- No painel do Supabase, clique em **New Project**.
- Escolha um nome para o projeto (ex: `cxpack-radar`).
- Defina uma **Senha de Banco de Dados** forte (guarde essa senha!).
- Escolha a região mais próxima (ex: *South America (São Paulo)*).

### 3. Copiar a String de Conexão (URI)
- No menu lateral do Supabase, acesse **Project Settings** -> **Database**.
- Role até a seção **Connection string** e selecione a aba **URI**.
- Copie o endereço completo. O formato será:
  ```text
  postgresql://postgres:[SUA_SENHA]@db.[SEU_PROJETO].supabase.co:5432/postgres
  ```
  *(Lembre-se de substituir `[SUA_SENHA]` pela senha que você criou no passo 2).*

### 4. Cadastrar a String de Conexão no CXPack Radar
Você tem duas opções fáceis:

#### Opção A (Pela Interface da Aplicação - Recomendado):
1. Abra o CXPack Radar e acesse a tela **Configurações (`0_settings`)**.
2. Na aba **Credenciais & Integrações**, cole a URL no campo **DATABASE_URL**.
3. Clique no botão **💾 SALVAR SUPABASE URL**.
4. Clique no botão **🧪 TESTAR BANCO** para confirmar a conexão com o Supabase.

#### Opção B (No arquivo `.streamlit/secrets.toml`):
Abra o arquivo `.streamlit/secrets.toml` e adicione a linha:
```toml
DATABASE_URL = "postgresql://postgres:SuaSenha@db.xyz.supabase.co:5432/postgres"
```

---

## 🔄 Migração Automática das Tabelas

O CXPack Radar utiliza o SQLAlchemy 2.x e o repositório de migrações automáticas. Assim que a `DATABASE_URL` do Supabase for salva, o sistema criará automaticamente todas as 14 tabelas no Supabase (empresas, contatos, decisores, CRM, equipe, buscas e logs)!
