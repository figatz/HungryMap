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
    page_title="Cities",
    page_icon="🏙️",
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

def city_restaurants (df):
    """Funçao retorna o numero de restaurantes por cidade"""
    city_restaurants = df.groupby(['city', 'country_name'])['restaurant_id'].count().reset_index()
    city_restaurants = city_restaurants.sort_values(by='restaurant_id', ascending=False).head(20)

    # Pegue os países únicos na ordem de aparição nas 20 cidades
    unique_countries = city_restaurants['country_name'].unique()
    palette = [COUNTRY_COLORS[country] for country in unique_countries]

    df_plot = city_restaurants.rename(columns={
        'city': 'City Name',
        'restaurant_id': 'Restaurants Count',
        'country_name': 'Country Name'
    })

    # Para garantir a ordem correta das barras (por quantidade de restaurantes)
    df_plot['City Name'] = pd.Categorical(df_plot['City Name'], categories=df_plot.sort_values('Restaurants Count', ascending=False)['City Name'], ordered=True)

    fig = px.bar(
        df_plot,
        x='City Name',
        y='Restaurants Count',
        color='Country Name',  # cor por país
        title='Top 20 cities with the most number of restaurants',
        color_discrete_sequence=palette,
        category_orders={'City Name': list(df_plot.sort_values('Restaurants Count', ascending=False)['City Name'])}
    )
    fig.update_layout(showlegend=True)
    fig.update_traces(textposition='auto')
    return fig

def city_restaurants_rating_low (df):
    """Retorna os restaurantes com as notas abaixo de 2.5"""
    # Calcula o total de restaurantes com nota <= 2.5 por cidade
    city_restaurants_rating_low = df.loc[df['aggregate_rating'] <= 2.5, ['city', 'country_name', 'aggregate_rating']]
    city_restaurants_rating_low = city_restaurants_rating_low.groupby(['city', 'country_name']).count().reset_index()
    city_restaurants_rating_low = city_restaurants_rating_low.sort_values(by='aggregate_rating', ascending=False).head(10)

    # Renomeia colunas para o gráfico
    df_plot = city_restaurants_rating_low.rename(columns={
        'city': 'City Name',
        'aggregate_rating': 'Restaurants Count',
        'country_name': 'Country Name'
    })

    # Garante a ordem das barras por quantidade de restaurantes
    df_plot['City Name'] = pd.Categorical(
        df_plot['City Name'],
        categories=df_plot.sort_values('Restaurants Count', ascending=False)['City Name'],
        ordered=True
    )

    # Paleta de cores dos países presentes no gráfico
    unique_countries = df_plot['Country Name'].unique()
    palette = [COUNTRY_COLORS[country] for country in unique_countries]

    fig = px.bar(
        df_plot,
        x='City Name',
        y='Restaurants Count',
        color='Country Name',
        title='Top 10 cities with the most restaurants rated 2.5/5.0 or below',
        color_discrete_sequence=palette,
        category_orders={'City Name': list(df_plot.sort_values('Restaurants Count', ascending=False)['City Name'])}
    )
    fig.update_layout(showlegend=True)
    fig.update_traces(textposition='auto')
    return fig

def city_restaurants_rating (df):
    """Retorna os restaurantes com as notas acima de 4"""
    city_restaurants_rating = df.loc[df['aggregate_rating'] >= 4, ['city', 'country_name', 'aggregate_rating']]
    city_restaurants_rating = city_restaurants_rating.groupby(['city', 'country_name']).count().reset_index()
    city_restaurants_rating = city_restaurants_rating.sort_values(by='aggregate_rating', ascending=False).head(10)
    # Renomeia colunas para o gráfico
    df_plot = city_restaurants_rating.rename(columns={
        'city': 'City Name',
        'aggregate_rating': 'Restaurants Count',
        'country_name': 'Country Name'
    })

    # Garante a ordem das barras por quantidade de restaurantes
    df_plot['City Name'] = pd.Categorical(
        df_plot['City Name'],
        categories=df_plot.sort_values('Restaurants Count', ascending=True)['City Name'],
        ordered=True
    )

    # Paleta de cores dos países presentes no gráfico
    unique_countries = df_plot['Country Name'].unique()
    palette = [COUNTRY_COLORS[country] for country in unique_countries]

    fig = px.bar(
        df_plot,
        x='City Name',
        y='Restaurants Count',
        color='Country Name',
        title='Top 10 cities with the most restaurants rated 4.0/5.0 or above',
        color_discrete_sequence=palette,
        category_orders={'City Name': list(df_plot.sort_values('Restaurants Count', ascending=False)['City Name'])}
    )
    fig.update_layout(showlegend=True)
    fig.update_traces(textposition='auto')
    return fig

def cuisine_types (df):
    """Top 20 cidades com mais tipos de culinária"""

    # Conta o número de tipos de culinária por cidade
    cuisines_types = df.groupby(['city', 'country_name'])['cuisines'].nunique().reset_index()
    cuisines_types = cuisines_types.sort_values(by='cuisines', ascending=False).head(20)

    # Renomeia colunas para o gráfico
    df_plot = cuisines_types.rename(columns={
        'city': 'City Name',
        'cuisines': 'Cuisines Types',
        'country_name': 'Country Name'
    })

    # Garante a ordem das barras por quantidade de tipos de culinária
    df_plot['City Name'] = pd.Categorical(
        df_plot['City Name'],
        categories=df_plot.sort_values('Cuisines Types', ascending=False)['City Name'],
        ordered=True
    )

    # Paleta de cores dos países presentes no gráfico
    unique_countries = df_plot['Country Name'].unique()
    palette = [COUNTRY_COLORS[country] for country in unique_countries]

    fig = px.bar(
        df_plot,
        x='City Name',
        y='Cuisines Types',
        color='Country Name',
        title='Top 20 cities with the most different cuisine types',
        color_discrete_sequence=palette,
        category_orders={'City Name': list(df_plot.sort_values('Cuisines Types', ascending=False)['City Name'])}
    )
    fig.update_layout(showlegend=True)
    fig.update_traces(textposition='auto')
    return fig

def city_avg_price (df):
    """Top 20 cidades com maior preço médio para dois"""
    # Top 20 cidades com maior preço médio para dois, ordenando por cidade e colorindo por país
    # Calcula o preço médio para dois por cidade e país
    city_avg_price = df.groupby(['city', 'country_name'])['average_cost_dolar'].mean().round(2).reset_index()
    city_avg_price = city_avg_price.sort_values(by='average_cost_dolar', ascending=False).head(20)

    # Renomeia colunas para o gráfico
    df_plot = city_avg_price.rename(columns={
        'city': 'City Name',
        'average_cost_dolar': 'Average Cost for Two (USD)',
        'country_name': 'Country Name'
    })

    # Garante a ordem das barras por preço médio
    df_plot['City Name'] = pd.Categorical(
        df_plot['City Name'],
        categories=df_plot.sort_values('Average Cost for Two (USD)', ascending=False)['City Name'],
        ordered=True
    )

    # Paleta de cores dos países presentes no gráfico
    unique_countries = df_plot['Country Name'].unique()
    palette = [COUNTRY_COLORS[country] for country in unique_countries]

    fig = px.bar(
        df_plot,
        x='City Name',
        y='Average Cost for Two (USD)',
        color='Country Name',
        title='Top 20 cities with the highest average cost for two (USD)',
        color_discrete_sequence=palette,
        category_orders={'City Name': list(df_plot.sort_values('Average Cost for Two (USD)', ascending=False)['City Name'])}
    )
    fig.update_layout(showlegend=True)
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
################### CITIES STREAMLIT #######################
############################################################

with st.container():
    st.title("🏙️ Cities information")
    st.markdown("#### All about the cities where you can find your favorite food")
    
with st.container(border=True):
    fig = city_restaurants(df)
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        fig = city_restaurants_rating(df)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    with st.container(border=True):
        fig = city_restaurants_rating_low(df)
        st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    fig = cuisine_types(df)
    st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    fig = city_avg_price(df)
    st.plotly_chart(fig, use_container_width=True)
