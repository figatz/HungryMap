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
    page_title="Home",
    page_icon="📈",
    layout="wide"
)

with st.spinner('Loading Data...'):
    
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
    
    #################################################
    ##################### MAP #######################
    #################################################
    
    #Map with all the restaurants marked
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    map_ = folium.Map(location=[center_lat, center_lon], zoom_start=2, control_scale=True)
    folium.TileLayer(tiles= 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}' ,
                     attr= 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012',
                     name= "Esri.WorldStreetMap").add_to(map_)
    marker_cluster = MarkerCluster().add_to(map_)
    
    def add_marker(row):
        popup_html = f"""<b>{row['restaurant_name']}</b><br>
        Rating: {row['aggregate_rating']}/5<br>
        Cuisine: {row['cuisines']}<br>
        Price: {row['price_type']}"""
        iframe = folium.IFrame(html=popup_html, width=250, height=120)
        folium.Marker(
            [row['latitude'], row['longitude']],
            popup=folium.Popup(iframe),
            icon=folium.Icon(icon='cutlery', prefix='glyphicon', icon_color='white', color=row['color_name'])
        ).add_to(marker_cluster)
    
    df.apply(add_marker, axis=1)
    
    
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
    
    #################################################
    ################ HOME STREAMLIT ##############
    #################################################
    
    st.title(''' :orange[HungryMap] ''')
    st.markdown("### Taste the world, one map at a time!")
    with st.spinner('Loading Data...'):
        with st.container():
            st.title('Overall Metrics')
            col1, col2, col3, col4, col5 = st.columns(5, gap='large')
            with col1:
                col1.metric(label='Total Restaurants', value=unique_restaurants, help='Total restaurants registered in our database')
        
            with col2:
                col2.metric(label='Countries', value=unique_countries, help='Total countries registered in our database')
            
            with col3:
                col3.metric(label='Total cities', value= unique_cities, help='Total cities registered in our database')
            with col4:
                col4.metric(label='Total reviews', value=f"{total_votes:,}", help='Total reviews registered in our database')
            with col5:
                col5.metric(label='Culinary diversity', value=total_cuisines, help='Total cuisines registered in our database')
                
        st.markdown("""---""")
    
    with st.spinner('Loading Data...'):
        with st.container():
            folium_static(map_, width=1920, height=600)
   
   
