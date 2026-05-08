**# TASKFLOW - Plataforma de Turnos Hospitalares

Sistema backend desenvolvido para conectar profissionais da saúde a unidades hospitalares com base em proximidade, disponibilidade e reputação profissional.

---

# Estrutura de Pastas

```text
.
|-- app.py
|-- config.py
|-- .env
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

---

# Responsabilidade de Cada Pasta

* `models/` → tabelas e entidades do banco de dados
* `routes/` → endpoints da API REST
* `services/` → regras de negócio 
* `utils.py` → funções auxiliares
* `config.py` → configurações e variáveis de ambiente
* `app.py` → ponto principal da aplicação Flask

---

# Funcionalidades Implementadas

* Cadastro de profissionais da saúde
* Cadastro de unidades hospitalares
* Criação de turnos
* Recomendação de profissionais para turnos
* Recomendação de turnos para profissionais
* Sistema de candidaturas
* Aceite, recusa e cancelamento de candidatura
* Conclusão de turnos
* Sistema de avaliações
* Atualização automática de reputação média

---

# Fluxo Principal da Plataforma

1. A unidade hospitalar realiza o cadastro
2. A unidade cria um turno
3. O profissional realiza o cadastro
4. O profissional consulta oportunidades
5. O profissional se candidata ao turno
6. A unidade aceita uma candidatura
7. O turno recebe status `preenchido`
8. Após conclusão do turno, ambas as partes podem se avaliar

---

# Modelos Principais

## Profissional

* Dados pessoais básicos
* Endereço completo
* Coordenadas
* Categoria profissional
* Preferência de turno
* Avaliação média

## UnidadeHospitalar

* Nome
* Endereço completo
* Coordenadas
* Avaliação média

## Turno

* Unidade responsável
* Categoria exigida
* Tipo de turno
* Valor
* Observações
* Status
* Datas opcionais
* Profissional confirmado

## Candidatura

* Profissional
* Turno
* Status
* Pontuação da candidatura
* Distância em KM

## Avaliação

* Turno relacionado
* Autor da avaliação
* Nota
* Comentário

---

# Integração com API Regional

Arquivo responsável:

```text
plataforma_turnos/services/location_provider.py
```

Funções preparadas:

* `resolve_coordinates`
* `calculate_distance_km`

## Configuração no `.env`

```env
LOCATION_PROVIDER=regional
REGIONAL_GEO_API_URL=https://sua-api/geocode
REGIONAL_DISTANCE_API_URL=https://sua-api/distance
REGIONAL_API_KEY=sua-chave
```

## Ajustes Prováveis

* parâmetros enviados para API
* autenticação/header
* formato do JSON retornado

O sistema atualmente já tenta interpretar:

* `latitude` e `longitude`
* `data.latitude` e `data.longitude`
* `distance_km`
* `data.distance_km`

---

# Endpoints Principais

## Profissionais

```http
POST /profissionais
GET /profissionais
GET /profissionais/<id>
GET /profissionais/<id>/oportunidades
GET /profissionais/<id>/candidaturas
```

## Unidades

```http
POST /unidades
GET /unidades
GET /unidades/<id>
GET /unidades/<id>/turnos
```

## Turnos

```http
POST /turnos
GET /turnos
GET /turnos/<id>
GET /turnos/<id>/matches
POST /turnos/<id>/concluir
```

## Candidaturas

```http
POST /turnos/<id>/candidaturas
GET /turnos/<id>/candidaturas
POST /candidaturas/<id>/aceitar
POST /candidaturas/<id>/recusar
POST /candidaturas/<id>/cancelar
```

## Avaliações

```http
POST /turnos/<id>/avaliacoes
GET /turnos/<id>/avaliacoes
```

---

# Exemplos de Payload

## Criar Profissional

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

## Criar Unidade

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

## Criar Turno

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

## Candidatar Profissional

```json
{
  "profissional_id": 1
}
```

## Registrar Avaliação

```json
{
  "autor_tipo": "unidade",
  "nota": 5,
  "comentario": "Profissional pontual e tecnico."
}
```

---

# Como Executar

## Instalar dependências

```bash
pip install -r requirements.txt
```

## Rodar aplicação Flask

```bash
flask --app app run
```

---

# Melhorias Futuras

* Autenticação JWT
* Dockerização da aplicação
* Testes automatizados
* Deploy em nuvem
* Swagger/OpenAPI
* Sistema de permissões

---

# Autor

Kaio Silva Nascimento

* GitHub: https://github.com/Kalycriaa
* LinkedIn: https://www.linkedin.com/in/kaio-silva-nascimento-74b0bb399/
**
