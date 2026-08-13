# 🚀 Guia Completo para Iniciantes: CXPack Radar

Bem-vindo ao **CXPack Radar**! Este guia foi feito especialmente para você que é iniciante em programação.
Siga o passo a passo abaixo para colocar o sistema para funcionar no seu computador sem complicações!

---

## 1. Como Criar sua Chave Gratuita da Gemini API

1. Acesse o site do Google AI Studio pelo link:
   👉 **[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)**
2. Faça login com sua conta do Google (Gmail).
3. Clique no botão azul **"Create API key"** (Criar chave de API).
4. Selecione ou crie um projeto padrão do Google Cloud e confirme.
5. Uma janela irá aparecer mostrando um código longo (exemplo: `AIzaSyD...`).
6. Clique no botão **"Copy"** (Copiar) para guardar essa chave.

---

## 2. Como Configurar a Chave no Programa

1. No computador, abra a pasta do projeto `cxpack-radar`.
2. Dentro da pasta `.streamlit`, você verá um arquivo chamado `secrets.toml.example`.
3. Crie um novo arquivo chamado exatamente `secrets.toml` dentro da pasta `.streamlit`.
4. Abra o arquivo `.streamlit/secrets.toml` em um bloco de notas ou editor e cole o seguinte texto:

```toml
GEMINI_API_KEY = "COLE_SUA_CHAVE_AQUI"
```

*(Substitua `COLE_SUA_CHAVE_AQUI` pela chave que você copiou no passo anterior, mantendo as aspas).*

---

## 3. Como Iniciar o Programa

1. Abra o Terminal ou Prompt de Comando (cmd).
2. Digite o seguinte comando para instalar as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

3. Em seguida, inicie o programa digitando o comando:

```bash
streamlit run streamlit_app.py
```

4. O sistema abrirá automaticamente uma janela no seu navegador de internet!

---

## 4. Como Testar se Tudo Está Funcionando

1. No menu do lado esquerdo da tela do programa, clique em **`0_settings`** (Configurações).
2. Na tela que se abre, você verá dois cartões com sinais:
   - **Gemini API:** Deve mostrar 🟢 **Configurado**.
   - **Banco de Dados:** Deve mostrar 🟢 **Conectado**.
3. Clique nos botões **TESTAR GEMINI** e **TESTAR BANCO**.
4. Se ambos mostrarem mensagens verdes de sucesso, seu programa está 100% pronto!

---

## 5. Como Fazer sua Primeira Pesquisa

1. No menu lateral esquerdo, clique em **`1_new_search`** (Nova Pesquisa).
2. Digite o produto que você quer encontrar (exemplo: `Frasco plástico`).
3. Digite o material e capacidade se souber (exemplo: Material `PET`, Capacidade `500 ml`).
4. Clique no botão **🚀 INICIAR PESQUISA**.
5. O sistema fará a busca no Google via Gemini sem desperdiçar sua cota e exibirá os fornecedores encontrados!

---

## 6. (Futuro) Como Conectar o Supabase e Publicar no Streamlit Cloud

Quando você quiser disponibilizar o programa online para sua equipe:

1. **Supabase (Banco Online)**:
   - Crie uma conta gratuita em [supabase.com](https://supabase.com).
   - Crie um novo projeto PostgreSQL e copie a URL de conexão (`DATABASE_URL`).
   - Adicione essa `DATABASE_URL` no seu arquivo `secrets.toml`. O sistema passará a usar o PostgreSQL automaticamente!
2. **Streamlit Community Cloud (Hospedagem Gratuita)**:
   - Suba o código para um repositório no GitHub.
   - Acesse [streamlit.io/cloud](https://streamlit.io/cloud) e conecte seu GitHub.
   - Adicione suas chaves na seção **Secrets** das configurações do aplicativo online.
