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
    page_title="Cuisines",
    page_icon="🍽️",
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


#################################################
################ SIDEBAR STREAMLIT ##############
#################################################

image = Image.open('restaurant.jpg')
st.sidebar.image(image, width=170, use_container_width=True)

st.sidebar.markdown("# RESTAURANT FINDER")
st.sidebar.markdown("## The easiest way to find the best restaurant around the world!")
st.sidebar.markdown("""---""")

quantity = st.sidebar.select_slider(
    "Choose the number of restaurants you want to view:",
    options=[5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100],
    value=30
)

#Filtro de quantidade de restaurantes
selected_lines = df.index < quantity

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
################### CUISINES STREAMLIT #####################
############################################################

with st.container():
    st.title("🍽️ Cuisines information")
    st.markdown("#### All about delicious cuisines you can find in the world!")
    
with st.container():
    cuisine = st.selectbox(
    "Choose the cuisine that you want to view information from:",
    df.loc[:, "cuisines"].unique().tolist(),
    index=1
)
    #Filtro de cozinhas
    selected_lines = df['cuisines'] == cuisine
    df = df.loc[selected_lines, :].copy()
    
with st.container():
    col1, col2, col3 = st.columns(3, gap='large')
    with col1:
        best_rate = df.loc[:,['aggregate_rating']].max()
        st.metric(label="Best rated restaurant", value=best_rate)
        
    with col2:
        worst_rate = df.loc[:,['aggregate_rating']].min()
        st.metric(label="Worst rated restaurant", value=worst_rate)        
        
    with col3:
        cuisine_price = df.loc[:, ['cuisines', 'average_cost_dolar']].groupby('cuisines').mean().sort_values('average_cost_dolar', ascending=False).round(2) 
        st.metric(label="Average price for two in USD", value=cuisine_price.iloc[0,0])
    
with st.container():   
    st.dataframe(df.loc[:, ["restaurant_name", "country_name", "average_cost_dolar", "currency", "cuisines", "aggregate_rating", "votes"]].sort_values("aggregate_rating", ascending=False))
    
