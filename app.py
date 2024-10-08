import streamlit as st
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests

model = joblib.load('model.pkl')

def predict_risco(carteira, operacoes, estado, sub_regiao, modalidade):
    data = pd.DataFrame({
        'CARTEIRA': [carteira],
        'OPERACOES': [operacoes],
        'ESTADO': [estado],
        'SUB_REGIAO': [sub_regiao],
        'MODALIDADE': [modalidade]
    })
    prediction = model.predict(data)
    return prediction[0]

st.title('RiskMap 🗺')
st.header('Previsão de Risco de Crédito por Tamanho da Carteira, Região e Modalidades')
st.write('''
Nesse aplicativo, iremos disponbilizar a grande oportunidade de você simular uma carteira de crédito,
com as características que mais se enquadram no seu negócio! Vamos começar? 📌

Preencha os dados abaixo e depois clique em prever, após isso, você terá a resposta se é uma característica de uma carteira de alto ou baixo risco.
''')

carteira = st.number_input('CARTEIRA', min_value=0)
operacoes = st.number_input('OPERACOES', min_value=0)

estados = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 
    'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 
    'SP', 'SE', 'TO'
]
#Tive que definir novamente as funções pois quando importava do 'services', sempre me gerava um erro no qual não consegui resolver
def get_bcb_data(file_path):
    response = requests.get(file_path)
    if response.status_code == 200:
        data = response.json()
        df = pd.json_normalize(data['value'])
        return df.dropna()
    else:
        raise ValueError(f"Erro na solicitação: {response.status_code}")

def risco_alto(risco):
    mapping = {'AA-C': '0', 'D-H': '1'}
    return mapping.get(risco)

caminho = 'https://olinda.bcb.gov.br/olinda/servico/scr_sub_regiao/versao/v1/odata/scr_sub_regiao(DataBase=@DataBase)?@DataBase=202407&$format=json&$select=DATA_BASE,CLIENTE,ESTADO,SUB_REGIAO,MODALIDADE,RISCO,OPERACOES,CARTEIRA'
df_bcb = get_bcb_data(caminho)
df_bcb['RISCO'] = df_bcb['RISCO'].apply(risco_alto)
df_bcb = df_bcb.drop(columns=['DATA_BASE'])

sub_regioes = df_bcb['SUB_REGIAO'].unique()
modalidades = df_bcb['MODALIDADE'].unique()

estado = st.selectbox('ESTADO', options=sorted(estados))
sub_regiao = st.selectbox('SUB REGIAO', options=sorted(sub_regioes))
modalidade = st.selectbox('MODALIDADE', options=sorted(modalidades))

if st.button('Prever'):
    risco = predict_risco(carteira, operacoes, estado, sub_regiao, modalidade)
    st.write(f'O risco previsto é: {risco}')

# Adicionando o gráfico de correlação
st.subheader('Gráfico de Correlação entre Volume de Carteira e Quantidade de Operações')

plt.figure(figsize=(10, 6))
sns.scatterplot(x='OPERACOES', y='CARTEIRA', hue='RISCO', data=df_bcb, palette='coolwarm', alpha=0.7)
plt.title('Correlação entre CARTEIRA e OPERACOES')
plt.xlabel('OPERACOES')
plt.ylabel('CARTEIRA')

st.pyplot(plt)

st.subheader('Amostra dos Dados Utilizados ⬇⬇⬇')
st.dataframe(df_bcb)

st.subheader('Links Correlacionados com o Projeto 🔗')
st.write('API utilizada no projeto: https://dadosabertos.bcb.gov.br/dataset/scr-por-sub-regiao')
st.write('O que faz parte da base de dados utilizada, e qual o objetivo? https://www.bcb.gov.br/estabilidadefinanceira/scr')