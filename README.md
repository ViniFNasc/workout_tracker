
# 🏋️ Low Volume Tracker

Aplicação local em Python + Streamlit para registrar e acompanhar o treino
**Upper/Lower 4x** (Upper I, Lower I, Upper II, Lower II).

## Funcionalidades

- **Plano de treino fixo**, extraído do programa Upper/Lower 4x: 4 treinos,
  27 exercícios, cada um com sua sequência de séries.
- Cada série já vem definida pelo plano — **travado**, não editável:
  método (Preparatória / Work-set / Muscle Round), % da carga de trabalho,
  faixa de repetições alvo, RIR-alvo, velocidade de execução e intervalo.
- Você só informa a **carga de trabalho (kg)** do exercício no dia e as
  **repetições realizadas** em cada série (RIR realizado é opcional) — tudo
  em formato de tabela, uma linha por série.
- A carga de cada série preparatória é calculada automaticamente como %
  da carga de trabalho informada.
- Aba **Plano de treino**: consulta somente leitura de toda a rotina
  (útil para conferir o próximo exercício, a observação de execução ou
  o substituto sugerido).
- Histórico completo com filtros por usuário, data, exercício, treino e método.
- Dashboard com métricas do último treino, evolução de carga por exercício
  e volume.
- Persistência local em CSV.
- Backup simples copiando a pasta `data`.
- **Login por usuário e senha.** Cada pessoa só registra treinos no seu próprio usuário, mas todos podem visualizar (Dashboard/Histórico) os treinos de qualquer usuário cadastrado.

## Como executar

Abra o terminal na pasta do projeto:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute:

```bash
streamlit run app.py
```

O navegador abrirá a aplicação.

## Usuários e login

O acesso é protegido por usuário e senha. Os usuários **não se cadastram sozinhos** —
você (administrador) cadastra cada pessoa manualmente no arquivo `data/usuarios.csv`.

O arquivo tem estas colunas:

| coluna          | descrição                                              |
|-----------------|---------------------------------------------------------|
| `usuario`       | login que a pessoa vai digitar (ex.: `joao`)             |
| `senha_hash`    | hash da senha (nunca a senha em texto puro)              |
| `nome_exibicao` | nome que aparece na sidebar (opcional; se vazio, usa `usuario`) |
| `ativo`         | `True` ou `False` — usuários inativos não conseguem logar |

### Como adicionar um usuário

1. Gere o hash da senha rodando, na pasta do projeto:

   ```bash
   python gerar_hash_senha.py
   ```

   Digite a senha quando solicitado. O script imprime um hash como:

   ```text
   4c94bd7240e61a20c60568f9aebe999e1d94b952ddc5dffeaa4db7257974a255
   ```

2. Abra `data/usuarios.csv` (pode editar em Excel, Bloco de Notas, etc.) e adicione
   uma linha, por exemplo:

   ```text
   usuario,senha_hash,nome_exibicao,ativo
   joao,4c94bd7240e61a20c60568f9aebe999e1d94b952ddc5dffeaa4db7257974a255,João,True
   ```

3. Salve o arquivo. Na próxima vez que a pessoa acessar o app, o login já funciona
   (não precisa reiniciar o Streamlit).

### Regras de acesso

- Cada usuário só consegue **registrar** treinos no seu próprio nome — não existe
  seleção de "para quem" registrar, o app usa automaticamente o usuário logado.
- Qualquer usuário pode **visualizar** o Dashboard e o Histórico de qualquer outro
  usuário cadastrado (há um seletor de usuário nessas telas).
- O plano de treino (exercícios, séries, %, alvos etc.) é o mesmo para todos e
  fica definido diretamente no código (`app.py`), não em um CSV editável — por
  isso os percentuais e demais valores do plano ficam travados na tela de registro.

## Estrutura

```text
treino_low_volume/
│
├── app.py
├── gerar_hash_senha.py
├── requirements.txt
├── README.md
│
└── data/
    ├── treinos.csv
    └── usuarios.csv
```

Os CSVs de dados (`treinos.csv`, `usuarios.csv`) são criados automaticamente na
primeira execução. Sem usuários cadastrados em `usuarios.csv`, ninguém consegue
entrar, então cadastre pelo menos um usuário antes de usar o app (veja acima).

## Backup

Para fazer backup, basta copiar a pasta:

```text
data/
```

O arquivo `treinos.csv` contém o histórico dos treinos e `usuarios.csv` contém os
logins cadastrados (com as senhas já em formato de hash — seguro para backup).
O plano de treino em si não precisa de backup: ele é parte do código (`app.py`).
