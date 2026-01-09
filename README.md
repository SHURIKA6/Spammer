# ShuraTools Pro v2.1 🛠️

O **ShuraTools** evoluiu. De um simples script de spam, agora ele é uma ferramenta completa de **Pentest, OSINT e Automação de Carga**. Desenvolvido para entusiastas de segurança e administradores de sistemas.

---

## ✨ O que há de novo na v2.0 Pro?

*   **🔍 OSINT Hunter**: Rastreie usuários em +4 plataformas e verifique vazamentos de e-mail (API Breach Check).
*   **📡 Port Scanner**: Verifique a segurança da sua rede escaneando portas abertas em IPs ou domínios.
*   **🌐 Auto-Proxy**: Busca automática de proxies HTTP/HTTPS em fontes públicas (não precisa mais de lista manual!).
*   **🎨 Terminal Moderno**: Interface colorida para facilitar a leitura de logs em tempo real.
*   **🚀 Multi-Threading Otimizado**: Distribuição inteligente de carga para máxima eficiência.

---

## 🚀 Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/SHURIKA6/ShuraTools.git

# Entre na pasta
cd ShuraTools

# Instale as dependências (Colorama, Requests, Faker)
pip install -r requirements.txt
```

---

## 🛠️ Como Usar

### 1. Investigação (OSINT)
Descubra a presença digital de um alvo através do username ou verifique vulnerabilidades em um e-mail.
```bash
python ShuraTools.py --osint --target @usuario_alvo
```

### 2. Scanner de Rede (PortScan)
Veja quais serviços estão rodando em um servidor.
```bash
python ShuraTools.py --scan --target 182.23.44.1
```

### 3. Teste de Carga / Spam (Mail)
Envie fluxos de requisições com rotação de identidade e proxy.
```bash
python ShuraTools.py --mail --target vitima@gmail.com --qty 100 --threads 20 --proxy
```

### 4. Denúncia Automática (Social)
Módulos de report para contenção de abusos em plataformas sociais.
```bash
python ShuraTools.py --zap --target 5511999999999 --qty 50
python ShuraTools.py --ig --target @usuario_alvo
```

---

## ⚙️ Argumentos e Opções

| Flag | Descrição |
| :--- | :--- |
| `--mail` | Ativa o módulo de Spam de E-mail. |
| `--osint` | Ativa o módulo de investigação de pegada digital. |
| `--scan` | Executa o port scanner no alvo. |
| `--zap` | Módulo de denúncia de WhatsApp. |
| `--ig` | Módulo de report de Instagram. |
| `--target` | Define o alvo (email, fone, @user ou IP). |
| `--qty` | Quantidade total de requisições/instâncias. |
| `--threads` | Número de processos simultâneos. |
| `--proxy` | Busca e usa proxies rotativos automaticamente. |
| `--timer` | Delay entre as ações (em segundos). |

---

## ⚠️ Aviso Legal (Disclaimer)

Esta ferramenta foi criada estritamente para fins **educacionais e testes autorizados**. O autor não se responsabiliza pelo uso indevido para fins ilícitos, assédio ou qualquer atividade que viole os termos de serviço das plataformas mencionadas. Use com ética e responsabilidade.

---
**Desenvolvido por Shura** 🛡️
