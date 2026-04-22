
# TASKFLOW - Plataforma de Turnos Hospitalares

## Estrutura de pastas no VS Code

```text
.
|-- app.py
|-- config.py
|-- .env.example
|-- requirements.txt
|-- README.md
`-- plataforma_turnos
    |-- __init__.py
    |-- extensions.py
    |-- utils.py
    |-- models
    |   |-- __init__.py
    |   |-- profissional.py
    |   |-- unidade.py
    |   |-- turno.py
    |   |-- candidatura.py
    |   `-- avaliacao.py
    |-- routes
    |   |-- __init__.py
    |   |-- health.py
    |   |-- profissionais.py
    |   |-- unidades.py
    |   |-- turnos.py
    |   |-- candidaturas.py
    |   `-- avaliacoes.py
    `-- services
        |-- __init__.py
        |-- location_provider.py
        |-- scoring.py
        `-- workflow.py
```

## O que cada pasta faz

- `models`: tabelas do banco
- `routes`: endpoints da API
- `services`: regras de negocio
- `utils.py`: funcoes pequenas de apoio
- `config.py`: configuracoes e variaveis de ambiente
- `app.py`: ponto de entrada para rodar o Flask

## O que foi incluido

- cadastro de profissionais
- cadastro de unidades hospitalares
- criacao de turnos
- recomendacao de profissionais para um turno
- recomendacao de turnos para um profissional
- candidaturas para turnos
- aceite, recusa e cancelamento de candidatura
- conclusao de turno
- avaliacao da unidade para o profissional
- avaliacao do profissional para a unidade
- atualizacao automatica da nota media de profissionais e unidades

## Fluxo principal do produto

1. a unidade se cadastra
2. a unidade cria um turno
3. o profissional se cadastra
4. o profissional consulta oportunidades
5. o profissional se candidata
6. a unidade aceita uma candidatura
7. o turno fica com status `preenchido`
8. ao terminar, a unidade conclui o turno
9. unidade e profissional avaliam um ao outro

## Modelos principais

### Profissional

- dados pessoais basicos
- endereco completo
- coordenadas
- categoria
- preferencia de turno
- avaliacao media
- taxa de aceitacao

### UnidadeHospitalar

- nome
- endereco completo
- coordenadas
- avaliacao media

### Turno

- unidade
- categoria exigida
- tipo do turno
- valor
- observacoes
- status
- datas opcionais
- profissional confirmado

### Candidatura

- profissional
- turno
- status
- pontuacao no momento da candidatura
- distancia em km

### Avaliacao

- turno
- autor da avaliacao
- nota
- comentario

## Onde conectar a API regional

O arquivo que voce deve editar para integrar sua API regional e:

- [plataforma_turnos/services/location_provider.py]

Esse arquivo ja esta preparado com dois pontos:

- `resolve_coordinates`: transforma endereco em latitude/longitude
- `calculate_distance_km`: calcula a distancia entre profissional e unidade

### Como ativar

No `.env`, troque:

```env
LOCATION_PROVIDER=regional
REGIONAL_GEO_API_URL=https://sua-api/geocode
REGIONAL_DISTANCE_API_URL=https://sua-api/distance
REGIONAL_API_KEY=sua-chave
```

### O que voce provavelmente vai ajustar

- nomes dos parametros enviados
- header de autenticacao
- formato do JSON de resposta

Hoje o projeto ja tenta ler:

- `latitude` e `longitude`
- ou `data.latitude` e `data.longitude`
- `distance_km`
- ou `data.distance_km`

Se a sua API responder diferente, basta adaptar esse unico arquivo.

## Endpoints principais

### Profissionais

- `POST /profissionais`
- `GET /profissionais`
- `GET /profissionais/<id>`
- `GET /profissionais/<id>/oportunidades`
- `GET /profissionais/<id>/candidaturas`

### Unidades

- `POST /unidades`
- `GET /unidades`
- `GET /unidades/<id>`
- `GET /unidades/<id>/turnos`

### Turnos

- `POST /turnos`
- `GET /turnos`
- `GET /turnos/<id>`
- `GET /turnos/<id>/matches`
- `POST /turnos/<id>/concluir`

### Candidaturas

- `POST /turnos/<id>/candidaturas`
- `GET /turnos/<id>/candidaturas`
- `POST /candidaturas/<id>/aceitar`
- `POST /candidaturas/<id>/recusar`
- `POST /candidaturas/<id>/cancelar`

### Avaliacoes

- `POST /turnos/<id>/avaliacoes`
- `GET /turnos/<id>/avaliacoes`

## Exemplos de payload

### Criar profissional

```json
{
  "nome": "Ana Souza",
  "categoria": "enfermeiro",
  "registro_conselho": "COREN-12345",
  "endereco": "Rua A, 123",
  "cidade": "Sao Paulo",
  "estado": "SP",
  "cep": "01000-000",
  "preferencia_turno": "noturno",
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

### Criar unidade

```json
{
  "nome": "Hospital Central",
  "endereco": "Av Principal, 500",
  "cidade": "Sao Paulo",
  "estado": "SP",
  "cep": "01310-100",
  "latitude": -23.5631,
  "longitude": -46.6544
}
```

### Criar turno

```json
{
  "unidade_id": 1,
  "categoria": "enfermeiro",
  "tipo_turno": "noturno",
  "valor": 450.0,
  "observacoes": "UTI adulto",
  "inicio_em": "2026-04-22T19:00:00",
  "fim_em": "2026-04-23T07:00:00"
}
```

### Candidatar profissional

```json
{
  "profissional_id": 1
}
```

### Registrar avaliacao

```json
{
  "autor_tipo": "unidade",
  "nota": 5,
  "comentario": "Profissional pontual e tecnico."
}
```

## Como rodar

```bash
pip install -r requirements.txt
flask --app app run
```

## Proximo passo recomendado

O backend agora esta pronto para:

- conectar sua API regional de geolocalizacao
- receber uma interface web ou mobile
- evoluir para autenticacao depois

Se quiser, o proximo passo natural e eu montar o frontend inicial em HTML/CSS/JS ou React consumindo esses endpoints.
