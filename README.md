# 🚀 GestaoIP

Sistema de monitoramento de dispositivos de rede desenvolvido em Python.

O GestaoIP monitora equipamentos através de seus endereços IP, detectando falhas, indisponibilidades e recuperações em tempo real. O objetivo é permitir que empresas sejam notificadas rapidamente quando dispositivos críticos, como impressoras, servidores, roteadores ou computadores, ficarem offline.

---

## ✨ Funcionalidades

- Monitoramento de dispositivos por IP
- Verificação periódica de disponibilidade
- Detecção de falhas consecutivas
- Detecção de recuperação automática
- Registro de eventos em SQLite
- Configuração simples via JSON
- Compatível com Linux e Windows

---

## 📂 Estrutura do Projeto

```text
gestaoip/

├── main.py
├── monitor.py
├── database.py
├── config.py

├── data/
│   ├── config.json
│   └── monitor.db

├── logs/

└── requirements.txt
