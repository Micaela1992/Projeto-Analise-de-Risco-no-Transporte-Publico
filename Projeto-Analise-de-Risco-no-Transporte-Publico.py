#!/usr/bin/env python
# coding: utf-8

# ## <center>Análise de Risco no Transporte Público</center>
# 
# ### Objetivo:
# O objetivo desse projeto é analisar os dados reais de incidentes de trânsito na cidade de Londres e compreender os padrões de pessoas que estão envolvidas ou os principais motivos que os acidentes ocorrem.
# Para mostrar que com poucas ferramentas conseguimos extrair informações valiosas dos dados, vou utilizar somente o Pandas e SQL para manipulação dos dados e o Matplotlib para criar as visualizações dos dados.
# 
# ### Fonte de dados:
# https://tfl.gov.uk/corporate/publications-and-reports/bus-safety-data

# ### Importando as bibliotecas necessárias

# In[1]:


import pandas as pd
import pandasql as psql
import plotly.express as px


# In[2]:


# Versões dos pacotes usados neste Jupyter Notebook
get_ipython().run_line_magic('reload_ext', 'watermark')
get_ipython().run_line_magic('watermark', '-a "Micaela" --iversions')


# ### Carregando o Dataframe e fazendo Data Wrangling

# In[3]:


df = pd.read_excel('TFL_Bus_Safety.xlsx')


# In[4]:


# Visualizando as 10 primeiras linhas
df.head(10)


# In[5]:


# Verificando a quantidade de linhas e colunas da base
df.shape


# In[6]:


# Verificando os nomes das colunas
df.columns


# Colunas com espaços entre os nomes podem nos dar problemas no decorrer da análise, então vou alterar os espaços por "_".

# In[7]:


df.rename(columns = lambda x: x.replace(' ', '_'), inplace = True)
df.head()


# In[8]:


# Informações gerais do dataframe
df.info()


# Conforme acima, já sabemos que não temos valores nulos em nenhuma coluna, então não devemos nos preocupar com este tipo de tratamento. Mas, por precaução, vou verificar se temos valores duplicados na base.

# In[9]:


df[df.duplicated(keep = 'first')]


# Temos valores duplicados na base, vou removê-los para que nossa análise seja próxima à realidade.

# In[10]:


# Removendo as observações duplicadas
df.drop_duplicates(inplace = True)


# ### Análise Exploratória dos Dados

# Vamos ter um overview sobre os acidentes ao longo do tempo. Para isso precisarei fazer alguns ajustes no dataframe.

# In[11]:


# Contando o número de incidentes por ano
query = """
SELECT Year, COUNT(*) AS Contagem
FROM df
GROUP BY Year;
"""

contagem_ano = psql.sqldf(query)

contagem_ano.head()


# In[12]:


# Criando um gráfico temporal dos incidentes ocorridos
fig = px.line(contagem_ano, x = contagem_ano['Year'], y = contagem_ano['Contagem'], hover_data = contagem_ano,
              title = 'Incidentes por ano', height = 400, width = 1000, line_shape = 'spline', markers = True)
fig.update_yaxes(title = 'Contagem', ticks = 'outside')
fig.update_xaxes(title = 'Ano', ticks = 'outside')
fig.show()


# Podemos ver que o pico de incidentes foi em 2017. Vamos investigar mais a fundo e entender esse comportamento com clareza.

# <b>Qual a quantidade de incidentes por gênero?

# In[13]:


query = """
SELECT Victims_Sex, COUNT(*) AS Contagem
FROM df
GROUP BY Victims_Sex;
"""

incidentes_genero = psql.sqldf(query)

incidentes_genero


# In[14]:


fig = px.bar(incidentes_genero, x = incidentes_genero.Victims_Sex, y = incidentes_genero.Contagem, color = 'Victims_Sex',
             title = 'Incidentes por gênero', hover_data = incidentes_genero, barmode = 'relative')
fig.update_yaxes(title = 'Contagem', ticks = 'outside')
fig.show()


# Mais de 50% das vitimas envolvidas neste incidentes são mulheres (sem considerar que nos desconhecidos ainda pode ter mulheres também). Será que o tipo de incidente tem relação com isso? Por exemplo, mulheres são mais sensíveis e geralmente têm menos força física do que homens, o que nos torna mais suscetíveis a assaltos, etc.

# <b>Qual faixa etária esteve mais envolvida nos incidentes?

# In[15]:


query = """
SELECT Victims_Age, COUNT(Victims_Age) AS Contagem
FROM df
GROUP BY Victims_Age
ORDER BY Contagem DESC
LIMIT 1
"""

faixa_etaria = psql.sqldf(query)

faixa_etaria


# In[16]:


# Query para o gráfico de pizza
query = """
SELECT Victims_Age, COUNT (Victims_Age) AS Contagem
FROM df
GROUP BY Victims_Age"""

# Executando a query e adicionando na variável que usarei na plotagem
fx_etaria_pizza = psql.sqldf(query)

fig = px.pie(data_frame = fx_etaria_pizza, names = 'Victims_Age', values = 'Contagem',
             title = 'Incidentes por faixa etária')
fig.show()


# Adultos levam a maior fatia desta pizza, o que faz todo sentido, pois estão ativos no trânsito no dia a dia, seja dirigindo, seja no transporte público para ir trabalhar, se locomover, etc.

# <b>Qual o percentual de incidentes por tipo de evento (Incident Event Type)?

# In[17]:


query = """
SELECT Incident_Event_Type,
       COUNT(Incident_Event_Type) AS Contagem,
       ROUND((CAST(COUNT(Incident_Event_Type) AS FLOAT) / 
       (SELECT COUNT(*) FROM df) * 100), 2) AS Percentual
FROM df
GROUP BY Incident_Event_Type
ORDER BY Contagem DESC
"""

por_evento = psql.sqldf(query)

por_evento


# In[18]:


fig = px.bar(por_evento, x = por_evento.Incident_Event_Type, y = por_evento.Percentual,
             color = 'Incident_Event_Type', hover_data = por_evento, barmode = 'relative',
             title = 'Tipo de incidente em %')
fig.update_yaxes(title = 'Percentual', ticks = 'outside')
fig.show()


# Curioso que 1/3 dos incidentes são relacionados à escorregões nas ruas. Um choque cultural pois aqui no Brasil (e inclusive eu no início do projeto) esperava que fossem mais relacionados à acidentes de trânsito ou assaltos.

# <b>Como foi a evolução de incidentes por mês ao longo do tempo?

# In[19]:


query = """
SELECT STRFTIME('%m/%Y', Date_Of_Incident) AS Mes,
       COUNT(Date_Of_Incident) AS Contagem
FROM df
GROUP BY Date_Of_Incident
"""

incidentes_mes = psql.sqldf(query)

incidentes_mes


# In[20]:


fig = px.line(incidentes_mes, x = 'Mes', y = 'Contagem', hover_data = incidentes_mes, line_shape = 'linear',
              markers = True, title = "Incidentes ao longo do tempo")
fig.update_yaxes(title = 'Contagem', ticks = 'outside')
fig.show()


# Como já sabemos, julho/2017 foi o mês com o maior pico de incidentes. Vamos averiguar quais foram os incidentes nesse período.

# In[21]:


query = """
SELECT Date_Of_Incident,
       Incident_Event_Type,
       COUNT(*) AS Contagem
FROM df
WHERE Date_Of_Incident BETWEEN '2017-07-01' AND '2017-08-01'
GROUP BY Incident_Event_Type
ORDER BY Contagem DESC
"""

tipo_incidente_2017 = psql.sqldf(query)

tipo_incidente_2017


# In[22]:


fig = px.bar(tipo_incidente_2017, x = 'Contagem', y = 'Incident_Event_Type',
             color = 'Incident_Event_Type', hover_data = tipo_incidente_2017, barmode = 'relative',
             title = 'Incidentes em 2017')
fig.update_yaxes(title = 'Tipo de incidente', ticks = 'outside')
fig.update_xaxes(title = 'Contagem', ticks = 'outside')
fig.show()


# Novamente escorregões estão no topo da lista, pelas minhas pesquisas esta época é a alta temporada em Londres, com temperatura ambiente mais altas e também com a abertura para visitação do Palácio de Buckingham e eles têm o Carnaval de Notting Hill (auto explicativo, pessoas passeando, descontraidas ou até mesmo bebendo).

# <b>Quando o incidente foi “Collision Incident” em qual mês houve o maior número de incidentes envolvendo pessoas do sexo feminino?

# In[23]:


query = """
SELECT STRFTIME('%m/%Y', Date_Of_Incident) AS Mes,
       COUNT(Date_Of_Incident) AS Contagem
FROM df
WHERE Incident_Event_Type = 'Collision Incident' AND Victims_Sex = 'Female'
GROUP BY Mes
ORDER BY Contagem DESC
LIMIT 1
"""

mulheres_colisoes = psql.sqldf(query)

mulheres_colisoes


# In[36]:


# Criando uma query para o gráfico
query = """
SELECT Date_Of_Incident,
       COUNT(Date_Of_Incident) AS Contagem
FROM df
WHERE Incident_Event_Type = 'Collision Incident' AND Victims_Sex = 'Female'
GROUP BY Date_Of_Incident
"""

grafico_mulheres_colisoes = psql.sqldf(query)

# Criando o gráfico
fig = px.line(grafico_mulheres_colisoes, x = 'Date_Of_Incident', y = 'Contagem', 
              hover_data = grafico_mulheres_colisoes, line_shape = 'linear', markers = True,
              title = 'Colisões envolvendo mulheres')
fig.update_yaxes(title = 'Contagem', ticks = 'outside')
fig.show()


# Por curiosidade, pesquisei na internet se aconteceu algo diferente em Londres em Nov/2016, e encontrei uma reportagem dizendo que houve um acidente de bonde, que infelizmente levou algumas pessoas à morte.
# 
# Fonte: https://veja.abril.com.br/mundo/acidente-de-bonde-deixa-7-mortos-e-50-feridos-em-londres

# <b>Qual foi a média de incidentes por mês envolvendo crianças (Child)?

# In[25]:


query = """
SELECT 
    Victims_Age,
    ROUND(AVG(Contagem), 2) AS Media
FROM (
    SELECT 
        STRFTIME('%Y-%m', Date_Of_Incident) AS Mes,
        Victims_Age,
        COUNT(*) AS Contagem
    FROM df
    GROUP BY Mes, Victims_Age
) AS subquery
GROUP BY Victims_Age;
"""

media = psql.sqldf(query)

media


# In[39]:


fig = px.bar(media, x = 'Victims_Age', y = 'Media', width = 800, height = 500,
             color = 'Victims_Age', hover_data = media, barmode = 'relative',
             title = 'Média de incidentes por mês e faixa etária')
fig.update_xaxes(title = 'Faixa Etária', ticks = 'outside')
fig.update_yaxes(title = 'Média', ticks = 'outside')
fig.show()


# Crianças e idosos têm as menores médias, na minha opinião faz sentido, visto que eles tendem a se locomover menos diariamente do que adultos e jovens (geralmente estes grupos possuem mais atividades diárias, como trabalhar, estudos, etc).

# <b>Considerando a descrição de incidente como “Injuries treated on scene” (coluna Injury Result Description), qual o total de incidentes de pessoas do sexo masculino e sexo feminino?

# In[27]:


query = """
SELECT Victims_Sex, COUNT(Victims_Sex) AS Contagem
FROM df
WHERE Injury_Result_Description = 'Injuries treated on scene'
GROUP BY Victims_Sex
"""

tratados_no_local = psql.sqldf(query)

tratados_no_local


# In[44]:


fig = px.pie(tratados_no_local, names = 'Victims_Sex', values = 'Contagem', hole = 0.7,
             title = 'Incidentes tratados no local por gênero')
fig.show()


# 50% dos incidentes tratados no local são em homens. Será que existe alguma explicação? Gostaria de ter mais informações nos dados para se aprofundar nesse asunto...

# <b>No ano de 2017 em qual mês houve mais incidentes com idosos (Elderly)?

# In[29]:


query = """
SELECT Year,
       STRFTIME('%Y-%m', Date_Of_Incident) AS Mes,
       Victims_Age,
       COUNT(Victims_Age) AS Contagem
FROM df
WHERE Year = '2017' AND Victims_Age = 'Elderly'
GROUP BY Mes
"""

idosos_2017 = psql.sqldf(query)

idosos_2017


# In[45]:


fig = px.line(idosos_2017, x = 'Mes', y = 'Contagem', hover_data = idosos_2017, line_shape = 'linear', 
              markers = True, title = "Incidentes com idosos em 2017")
fig.update_yaxes(title = 'Contagem', ticks = 'outside')
fig.show()


# Em julho o número de idosos envolvidos em acidentes são maiores em relação aos outros meses do ano. Fiz uma rápida pesquisa e li que nessa época do ano as temperaturas são um pouco mais agradáveis. Acredito que isso explique, pois assim os idosos ficam mais tendenciosos a sair para passeios, etc, gerando mais probabilidades de acidentes.

# <b>Considerando o Operador qual a distribuição de incidentes ao longo do tempo?

# In[31]:


query = """
SELECT Date_Of_Incident,
       Operator,
       COUNT(Date_Of_Incident) AS Contagem
FROM df
GROUP BY Date_Of_Incident, Operator
"""

incidentes_operador = psql.sqldf(query)

incidentes_operador


# In[46]:


fig = px.line(incidentes_operador, x = 'Date_Of_Incident', y = 'Contagem', hover_data = incidentes_operador,
              line_shape = 'spline', color = 'Operator',
              title = 'Incidentes por operador ao longo do tempo')
fig.show()


# Arriva London North é o operador mais envolvido em incidentes.

# <b>Qual o tipo de incidente mais comum com ciclistas?

# In[33]:


query = """
SELECT Victim_Category,
       Incident_Event_Type,
       COUNT(Victim_Category) AS Contagem
FROM df
WHERE Victim_Category = 'Cyclist'
GROUP BY Incident_Event_Type
ORDER BY Contagem DESC
"""

incidentes_ciclistas = psql.sqldf(query)

incidentes_ciclistas


# In[53]:


fig = px.bar(incidentes_ciclistas, x = 'Contagem', y = 'Incident_Event_Type', width = 800, height = 500,
             color = 'Incident_Event_Type', hover_data = incidentes_ciclistas, barmode = 'stack',
             title = 'Tipos de incidentes envolvendo ciclistas')
fig.update_xaxes(title = 'Contagem', ticks = 'outside')
fig.update_yaxes(title = 'Tipo de incidente', ticks = 'outside')
fig.show()


# Colisões estão na frente dos demais tipos de incidentes em disparado, acredito que precisam rever as leis de trânsito para ciclistas (ou que envolvam ciclistas), pois realmente tem algo errado.
