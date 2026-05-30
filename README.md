# 🚀 GestaoIP

Sistema de monitoramento inteligente de dispositivos de rede desenvolvido em Python.

O GestaoIP monitora equipamentos via IP em tempo real, detectando indisponibilidades e recuperações automaticamente. Ele é ideal para ambientes corporativos que precisam garantir disponibilidade de impressoras, servidores, roteadores e estações de trabalho, com envio de alertas em tempo real via WhatsApp.

---

## 📡 Funcionalidades

- Monitoramento contínuo de dispositivos por IP
- Detecção de queda de conexão (offline)
- Detecção automática de recuperação (online)
- Sistema de alertas em tempo real via WhatsApp
- Registro de logs e histórico de monitoramento
- Persistência de dados via SQLite
- Configuração simples via arquivo JSON
- Compatível com Linux e Windows

---

## ⚙️ Tecnologias utilizadas

- Python 3
- SQLite
- JSON para configuração
- Threads para monitoramento contínuo
- API de WhatsApp (Twilio ou integração similar)

---

## 📁 Estrutura do projeto

gestaoip/
├── main.py              # Ponto de entrada do sistema
├── monitor.py           # Lógica de monitoramento de IPs
├── database.py          # Gerenciamento do banco SQLite
├── config.py            # Configurações do sistema
├── whatsapp.py          # Integração de alertas via WhatsApp

├── data/
│   ├── config.json      # Configuração dos dispositivos
│   └── monitor.db       # Banco de dados SQLite

├── logs/                # Logs do sistema
├── requirements.txt
└── README.md

---

## 🚀 Como executar

# clonar repositório
git clone https://github.com/HenriqueC-r/GestaoIP.git

# entrar na pasta
cd GestaoIP

# criar ambiente virtual
python -m venv .venv

# ativar ambiente virtual (Linux/Mac)
source .venv/bin/activate

# ativar ambiente virtual (Windows)
.venv\Scripts\activate

# instalar dependências
pip install -r requirements.txt

# executar sistema
python main.py

---

## 📌 Próximas melhorias (roadmap)

- [ ] Dashboard web (Flask ou FastAPI)
- [ ] Interface gráfica
- [ ] Multiusuário
- [ ] Exportação de relatórios

---

## 👨‍💻 Autor

Desenvolvido por Caio 🚀  
Sistema em evolução contínua focado em automação e monitoramento de redes.
