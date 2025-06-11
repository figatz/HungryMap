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
    page_title="Countries",
    page_icon="🌎",
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

#  Retornar restaurantes de uma culinaria especifica com maior e menor nota encontrada ordenados pelo restaurant_id.
def best_rated_restaurants_by_cuisine(df, cuisine):
    """
    Retorna restaurantes de uma culinária específica com a maior nota encontrada, ordenados pelo restaurant_id.
    """
    filtered = df.loc[df['cuisines'] == cuisine, ['restaurant_name', 'restaurant_id', 'aggregate_rating']]
    if filtered.empty:
        return filtered  # Retorna vazio se não houver restaurantes dessa culinária
    max_rating = filtered['aggregate_rating'].max()
    best = filtered.loc[filtered['aggregate_rating'] == max_rating]
    return best.sort_values(by='restaurant_id', ascending=True)

def worst_rated_restaurants_by_cuisine(df, cuisine):
    """
    Retorna restaurantes de uma culinária específica com a menor nota encontrada, ordenados pelo restaurant_id.
    """
    filtered = df.loc[df['cuisines'] == cuisine, ['restaurant_name', 'restaurant_id', 'aggregate_rating']]
    if filtered.empty:
        return filtered  # Retorna vazio se não houver restaurantes dessa culinária
    min_rating = filtered['aggregate_rating'].min()
    worst = filtered.loc[filtered['aggregate_rating'] == min_rating]
    return worst.sort_values(by='restaurant_id', ascending=True)

#Numero de restaurantes unicos
unique_restaurants = df['restaurant_id'].nunique()
#Numero de países unicos
unique_countries = df['country_name'].nunique()
#Numero de cidades unicos
unique_cities = df['city'].nunique()
#Total de avaliações feitas
total_votes = df['votes'].sum()
#Numero de tipos de culinárias unicos
total_cuisines = df['cuisines'].nunique()

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


def most_restaurants_country (df):
    """Retorna a quantidade de restaurantes registrados por país"""
    most_restaurants_count = df.loc[:, ['country_name', 'restaurant_id']].groupby('country_name').agg({'restaurant_id': 'nunique'}).reset_index()
    most_restaurants_count = most_restaurants_count.sort_values(by='restaurant_id', ascending=False).reset_index(drop=True)
    palette = get_country_palette(most_restaurants_count['country_name'])
    
    df_plot = most_restaurants_count.rename(columns={
        'country_name': 'Country Name',
        'restaurant_id': 'Restaurants'
        })

    fig = px.bar(
        df_plot,
        x='Country Name',
        y='Restaurants',
        title='Quantity of restaurants registered in each country',
        text='Restaurants',
        color='Country Name',
        color_discrete_sequence=palette
        )
    fig.update_layout(showlegend=False)
    fig.update_traces(textposition='auto')
    return fig

def country_city_counts(df):
    """Retorna a quantidade de cidades registradas por país"""
    country_city_counts = df.loc[:, ['country_name', 'city']].groupby('country_name').agg({'city': 'nunique'}).reset_index()
    country_city_counts = country_city_counts.sort_values(by='city', ascending=False).reset_index(drop=True)
    palette = get_country_palette(country_city_counts['country_name'])

    df_plot = country_city_counts.rename(columns={
        'city': 'Cities',
        'country_name': 'Country Name'
    })
    
    fig = px.bar(
        df_plot,
        x='Country Name',
        y='Cities',
        orientation='v',
        title='Number of Cities registered per Country',
        color='Country Name',
        text='Cities',
        color_discrete_sequence=palette
    )
    fig.update_layout(showlegend=False)
    fig.update_traces(textposition='auto')
    return fig

def avg_price_for_two (df):
    """Retorna o preço médio de um prato para dois por país"""
    
    avg_price_for_two = df.loc[:, ['country_name', 'average_cost_dolar']].groupby(['country_name']).agg({'average_cost_dolar': 'mean'}).round(2)
    avg_price_for_two = avg_price_for_two.sort_values(by='average_cost_dolar', ascending=False).reset_index()

    palette = get_country_palette(avg_price_for_two['country_name'])

    df_plot = avg_price_for_two.rename(columns={
            'average_cost_dolar': 'Cost in US Dollars',
            'country_name': 'Country Name'
        })

    fig = px.bar(
        df_plot,
        x='Country Name',
        y='Cost in US Dollars',
        title='Average price for two in USD',
        color='Country Name',
        text='Cost in US Dollars',
        color_discrete_sequence=palette
    )
    fig.update_layout(showlegend=False)
    fig.update_traces(textposition='auto')
    return fig

def avg_score (df):
    """Retorna a média de avaliações por país"""
    avg_score = df.loc[:,['country_name', 'aggregate_rating']].groupby('country_name').mean().round(2)
    avg_score = avg_score.sort_values(by='aggregate_rating', ascending=False).reset_index()

    palette = get_country_palette(avg_score['country_name'])
    df_plot = avg_score.rename(columns={
            'aggregate_rating': 'Rating (0-5)',
            'country_name': 'Country Name'
        })

    fig = px.bar(
        df_plot,
        x='Country Name',
        y='Rating (0-5)',
        title='Average Rating (0-5) by Country',
        color='Country Name',
        text='Rating (0-5)',
        color_discrete_sequence=palette
    )
    fig.update_layout(showlegend=False)
    fig.update_traces(textposition='auto')
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
################ COUNTRIES STREAMLIT #######################
############################################################
with st.container():
    st.title("🌎Countries data")
    st.markdown("#### All about the countries where you can find your favorite food")

with st.container(border=True):
    fig = most_restaurants_country(df)
    st.plotly_chart(fig, use_container_width=True)
    
with st.container(border=True):
    fig = country_city_counts(df)
    st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        fig = avg_price_for_two(df)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = avg_score(df)
        st.plotly_chart(fig, use_container_width=True)