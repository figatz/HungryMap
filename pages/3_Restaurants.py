import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import inflection
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

st.set_page_config(
    page_title="Restaurants",
    page_icon="🍴",
    layout="wide"
)

# Carregar o dataset
# Certifique-se de que o arquivo train.csv está no mesmo diretório do script
df1 = pd.read_csv('zomato.csv')
df = df1.copy()
#######################################
########## LIMPEZA DOS DADOS ##########
#######################################

df = df.drop_duplicates(subset=['Restaurant ID', 'Restaurant Name', 'Address', 'Votes'])
#Renomeando as colunas
def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df
df = rename_columns(df)

df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0] if isinstance(x, str) else x)

#Retirando valores zerados da coluna average_cost_for_two
df = df.loc[df['average_cost_for_two'] != 0, :]
#Retirando valores nulos da coluna cuisines
df.dropna( subset=['cuisines'], inplace=True)
df = df.reset_index(drop=True)

##########################################
############ FUNCTIONS ###################
##########################################

# Atribuir cores aos ratings
COLORS = {
 "3F7E00": "darkgreen",
 "5BA829": "green",
 "9ACD32": "lightgreen",
 "CDD614": "orange",
 "FFBA00": "red",
 "CBCBC8": "darkred",
 "FF7800": "darkred",
 }
def color_name(color_code):
    return COLORS[color_code]

color_name_vectorized = np.vectorize(color_name)
df['color_name'] = color_name_vectorized(df['rating_color'])

#Coluna com o nome dos países
COUNTRIES = {
 1: "India",
 14: "Australia",
 30: "Brazil",
 37: "Canada",
 94: "Indonesia",
 148: "New Zeland",
 162: "Philippines",
 166: "Qatar",
 184: "Singapure",
 189: "South Africa",
 191: "Sri Lanka",
 208: "Turkey",
 214: "United Arab Emirates",
 215: "England",
 216: "United States of America",
 }
def country_name(country_id):
    return COUNTRIES[country_id]

country_name_vectorized = np.vectorize(country_name)
df['country_name'] = country_name_vectorized(df['country_code'])

#Determinaçao do tipo de preço
def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

create_price_tye = np.vectorize(create_price_tye)
df['price_type'] = create_price_tye(df['price_range'])

#Correction of a wrong value in the average cost for two column
df.loc[350, 'average_cost_for_two'] = 120

#Adição do dolar australiano e cambio de moedas para dolar
df.loc[df['country_code'] == 14, 'currency'] = 'Australian Dollar'
taxas_cambio = {
    "Dollar($)": 1.00,
    "Botswana Pula(P)": 13.38, 
    "Brazilian Real(R$)": 5.56,
    "Emirati Diram(AED)": 3.67, 
    "Indian Rupees(Rs.)": 85.79,
    "Indonesian Rupiah(IDR)": 16258.05,
    "NewZealand($)":1.65,
    "Pounds(£)": 0.74,
    "Qatari Rial(QR)": 3.64,
    "Rand(R)": 17.78,
    "Sri Lankan Rupee(LKR)": 299.17,
    "Turkish Lira(TL)": 39.28,
    "Australian Dollar": 1.54    
}

def converter_para_dolar(valor, moeda_origem):
    if moeda_origem in taxas_cambio:
        taxa_cambio = taxas_cambio[moeda_origem]
        valor_em_dolar = valor / taxa_cambio
        return valor_em_dolar
    else:
        return None
    
df['average_cost_dolar'] = df.apply(lambda linha: converter_para_dolar(linha['average_cost_for_two'], linha['currency']), axis=1)
df['average_cost_dolar'] = df['average_cost_dolar'].round(2)

# Paleta de cores graficos
COUNTRY_COLORS = {
    "India": "#719BF7",                
    "Australia": "#E68435",            
    "Brazil": "#F1E209",               
    "Canada": "#6B4AFF",               
    "Indonesia": "#7389CF",            
    "New Zeland": "#00F3FB",           
    "Philippines": "#BB3C3C",          
    "Qatar": "#F5ACC4",                
    "Singapure": "#FAEF8E",            
    "South Africa": "#F4511E",         
    "Sri Lanka": "#81D376",            
    "Turkey": "#E0E1E9",               
    "United Arab Emirates": "#28EE0E", 
    "England": "#EB6DBB",              
    "United States of America": "#0059BF" 
}
def get_country_palette(country_list):
    return [COUNTRY_COLORS[country] for country in country_list]

#Resutarantes com mais votos
most_reviews = df.loc[:, ['restaurant_name', 'votes', 'city', 'country_name']].sort_values(by='votes', ascending=False).reset_index(drop=True)

#Restaurantes com melhor avaliação
best = df.loc[df['aggregate_rating'] >= 4.9, ['restaurant_name','restaurant_id','aggregate_rating','city','country_name']]
best = best.sort_values(by=['restaurant_id'], ascending=True, na_position='last').reset_index(drop=True)

def votes (df):
    # Calcula a média de votos para restaurantes com e sem online delivery
    votes_online = df.loc[df['has_online_delivery'] == 1, 'votes'].mean().astype(int)
    votes_no_online = df.loc[df['has_online_delivery'] == 0, 'votes'].mean().astype(int)

    # Prepara os dados para o gráfico
    pie_data = pd.DataFrame({
        'Delivery Type': ['Online Delivery', 'No Online Delivery'],
        'Average Votes': [votes_online, votes_no_online]
    })
    colors = ['#1976D2', '#D32F2F']
    # Plota o gráfico de pizza mostrando o número de votos
    fig = px.pie(
        pie_data,
        names='Delivery Type',
        values='Average Votes',
        title='Average number of votes: Online Delivery vs No Online Delivery',
        color='Delivery Type',
        color_discrete_map={
            'Online Delivery': '#1976D2',      # azul
            'No Online Delivery': "#D82222"    # vermelho
    })
    fig.update_traces(textinfo='label+value')  # Mostra o nome e o valor absoluto
    return fig

def restaurant_price_classification(df):
    restaurant_price_classification = df.loc[:, ['price_type']].groupby('price_type').value_counts()
    
    fig = px.pie(restaurant_price_classification.reset_index(), values='count', names='price_type', title='Distribution of Restaurants by Price Classification', hole=0.3)
    fig.update_traces(textinfo='percent+label', # Exibe a porcentagem e o nome da fatia
                    textposition='inside',      # Posiciona o texto dentro da fatia
                    textfont_size=12) 
    return fig
#################################################
################ SIDEBAR STREAMLIT ##############
#################################################

image = Image.open('restaurant.jpg')
st.sidebar.image(image, width=170, use_container_width=True)

st.sidebar.markdown("# RESTAURANT FINDER")
st.sidebar.markdown("## The easiest way to find the best restaurant around the world!")
st.sidebar.markdown("""---""")


country_options = st.sidebar.multiselect(
    "Choose the countries that you want to view information from:",
    df.loc[:, "country_name"].unique().tolist(),
    default= df.loc[:, "country_name"].unique().tolist()
)
#Filtro de países
selected_lines = df['country_name'].isin(country_options)
df = df.loc[selected_lines, :].copy()

st.sidebar.markdown("""---""")

price_options = st.sidebar.multiselect(
    "Choose the price category that you want to view information from:",
    df.loc[:, "price_type"].unique().tolist(),
    default=["expensive", "normal", "cheap", "gourmet"]
)
#Filtro de preço
selected_lines = df['price_type'].isin(price_options)
df = df.loc[selected_lines, :].copy()

st.sidebar.markdown("""---""")

image = Image.open('fg_.png')
st.sidebar.image(image, width=170, use_container_width=True)
st.sidebar.markdown("#### Powered by Filipe Gatz")

############################################################
################ RESTAURANTS STREAMLIT #####################
############################################################

with st.container():
    st.title("Restaurants info")
    st.markdown("#### All about the restaurants where you can find your favorite food")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
    "Most reviewed restaurant",
    value=most_reviews.loc[0, 'restaurant_name'],
    delta=f"{int(most_reviews.loc[0, 'votes'])} votes",
    help=f"City: {most_reviews.loc[0, 'city']} | Country: {most_reviews.loc[0, 'country_name']}"
)
with col2:
    best = df.loc[df['aggregate_rating'] >= 4.9, ['restaurant_name','restaurant_id','aggregate_rating','city','country_name']]
    best = best.sort_values(by=['restaurant_id'], ascending=True, na_position='last').reset_index(drop=True)
    st.metric(
    "Best rating restaurant",
    value=best.loc[0, 'restaurant_name'],
    delta=f"{best.loc[0, 'aggregate_rating']} rating",
    help=f"City: {best.loc[0, 'city']} | Country: {best.loc[0, 'country_name']}"
)
with col3:
    expensive_restaurant = df.loc[:, ['restaurant_name', 'average_cost_dolar','city', 'country_name']].sort_values(by='average_cost_dolar', ascending=False).reset_index(drop=True)
    st.metric(
    "Most expensive restaurant",
    value=expensive_restaurant.loc[0, 'restaurant_name'],
    delta=f"{expensive_restaurant.loc[0, 'average_cost_dolar']} USD",
    help=f"City: {expensive_restaurant.loc[0, 'city']} | Country: {expensive_restaurant.loc[0, 'country_name']}"
)
with col4:
    cheapest_restaurant = df.loc[:, ['restaurant_name', 'average_cost_dolar','city', 'country_name']].sort_values(by='average_cost_dolar', ascending=True).reset_index(drop=True)
    st.metric(
    "Cheapest restaurant",
    value=cheapest_restaurant.loc[0, 'restaurant_name'],
    delta=f"{cheapest_restaurant.loc[0, 'average_cost_dolar']} USD",
    help=f"City: {cheapest_restaurant.loc[0, 'city']} | Country: {cheapest_restaurant.loc[0, 'country_name']}",
    delta_color="inverse"
)

with st.container(border=True):
    fig = votes(df)
    st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    fig = restaurant_price_classification(df)
    st.plotly_chart(fig, use_container_width=True)
