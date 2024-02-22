import pandas as pd
import plotly.express as px
import streamlit as st
import luas.api
from luas.api import LuasLine, LuasDirection
import urllib.request, json

from operator import itemgetter


luas_client = luas.api.LuasClient()
global BUS_ID
global CALL_GTFSR
st.set_page_config(page_title="Transport", page_icon=":station:", layout="wide")
stations_filters = [
    "HIN - Heuston",
    "HCT - Heuston",
    "TPT - The Point",
    "SDK - Spencer Dock",
    "MYS - Mayor Square - NCI",
    "GDK - George's Dock",
    "CON - Connolly",
    "BUS - Busáras",
    "ABB - Abbey Street",
    "JER - Jervis",
    "FOU - Four Courts",
    "SMI - Smithfield",
    "MUS - Museum",
    "HEU - Heuston",
    "JAM - James's",
    "FAT - Fatima",
    "RIA - Rialto",
    "SUI - Suir Road",
    "GOL - Goldenbridge",
    "DRI - Drimnagh",
    "BLA - Blackhorse",
    "BLU - Bluebell",
    "KYL - Kylemore",
    "RED - Red Cow",
    "KIN - Kingswood",
    "BEL - Belgard",
    "COO - Cookstown",
    "HOS - Hospital",
    "TAL - Tallaght",
    "FET - Fettercairn",
    "CVN - Cheeverstown",
    "CIT - Citywest Campus",
    "FOR - Fortunestown",
    "SAG - Saggart",
    "DEP - Depot",
    "STX - St. Stephen's Green",
    "BRO - Broombridge",
    "CAB - Cabra",
    "PHI - Phibsborough",
    "GRA - Grangegorman",
    "BRD - Broadstone - DIT",
    "DOM - Dominick",
    "PAR - Parnell",
    "OUP - O'Connell - Upper",
    "OGP - O'Connell - GPO",
    "MAR - Marlborough",
    "WES - Westmoreland",
    "TRY - Trinity",
    "DAW - Dawson",
    "STS - St. Stephen's Green",
    "HAR - Harcourt",
    "CHA - Charlemont",
    "RAN - Ranelagh",
    "BEE - Beechwood",
    "COW - Cowper",
    "MIL - Milltown",
    "WIN - Windy Arbour",
    "DUN - Dundrum",
    "BAL - Balally",
    "KIL - Kilmacud",
    "STI - Stillorgan",
    "SAN - Sandyford",
    "CPK - Central Park",
    "GLE - Glencairn",
    "GAL - The Gallops",
    "LEO - Leopardstown Valley",
    "BAW - Ballyogan Wood",
    "RCC - Racecourse",
    "CCK - Carrickmines",
    "BRE - Brennanstown",
    "LAU - Laughanstown",
    "CHE - Cherrywood",
    "BRI - Bride's Glen",
]


if "destination" not in st.session_state:
    st.session_state.destination = []

if "trip_update"not in st.session_state:
    st.session_state.tripupdate=[]

if "bus_stops"not in st.session_state:
    st.session_state.bus_stops=[]

def int_try_parse(value):
    try:
        int(value)
        return True
    except:
        return False
def remove_spaces_from_list(lst):
    return [s.replace(' ', '') for s in lst]

def parse_bus_payload(x):

    id_str = "{:}".format(x["id"])
    id_str_wo_spaces = remove_spaces_from_list(id_str)
    return id_str

def get_bus_status(x):
    if(x["id"]==BUS_ID):
        
        start_time_str = x["trip_update"]["trip"]["start_time"]
        start_date_str = x["trip_update"]["trip"]["start_date"]
        schedule_str = x["trip_update"]["trip"]["schedule_relationship"]
        route_id_str = x["trip_update"]["trip"]["route_id"]
        # st.write(start_time_str)
        # st.write(start_date_str)
        result = f"{start_time_str} {start_date_str} {schedule_str} {route_id_str}"
        st.write("**Starting Time**:",start_time_str)
        st.write("**Starting Date**:",start_date_str)
        st.write("**Schedule Relationship**:",schedule_str)
        st.write("**Route ID**:",route_id_str)
        
        bus_stop_list=x["trip_update"]["stop_time_update"]
        
        bus_stop_List=get_bus_stop_det(bus_stop_list)
        

        # print(bus_stop_List)
        updated_bus_stop_List = ["Stop ID:"+x  for x in bus_stop_List]
        # print(updated_bus_stop_List)
        st.session_state.bus_stops.extend(updated_bus_stop_List)
        
        return result    


            



# ---- READ EXCEL ----
@st.cache_data
def get_data_from_luas():
    df = pd.read_excel(
        io="Passenger Journeys by Luas.xlsx",
        engine="openpyxl",
        sheet_name="Unpivoted",
        # skiprows=3,
        usecols="C:H",
        nrows=793,
    )

    return df

def get_data_from_buses():
    df = pd.read_excel(
        io="Passenger Journeys By Bus.xlsx",
        engine="openpyxl",
        sheet_name="Unpivoted",
        # skiprows=3,
        usecols="C:H",
        nrows=1075,
    )

    return df
# ---- Call API for GTFSR ----
@st.cache_resource
def Call_GTFSR():
    try:
        url = "https://api.nationaltransport.ie/gtfsr/v2/gtfsr?format=json"

        hdr ={
        # Request headers
        'Cache-Control': 'no-cache',
        'x-api-key': '895c3d8d3b334ae68d62acc08a42404a',
        }
        
        req = urllib.request.Request(url, headers=hdr)

        req.get_method = lambda: 'GET'
        
        with urllib.request.urlopen(req) as response:
          data = json.loads(response.read().decode('utf8'))

        with open('data.json', 'w') as f:
          json.dump(data, f, ensure_ascii=False, indent=4)

        print(response.getcode())

        print("Json File Written.")
    except Exception as e:
        print(e)

def parse_destination_payload(x):
    outbound = "↗️"
    inbound = "↙️"
    direction_str = outbound if x["direction"] == "Outbound" else inbound
    destination_str = "{: ^30}".format(x["destination"])
    due_str = "| " + x["due"] + " mins" if int_try_parse(x["due"]) else ""
    result = f"{direction_str} {destination_str} {due_str}"
    return result


def get_stop_details():
    filter_name = st.session_state["stops"]
    stop_details = luas_client.stop_details(filter_name.split(" - ")[0])
    stringified_json = json.dumps(stop_details)
    data_dict = json.loads(stringified_json)
    trams = data_dict["trams"]
    destinations_list = list(map(parse_destination_payload, trams))
    st.session_state.destination.extend(destinations_list)



def get_bus_stop_det(Bus_List):
    
    stop_id_list = list(map(itemgetter("stop_id"), Bus_List))
    return stop_id_list



    
df_luas = get_data_from_luas()
df_bus = get_data_from_buses()

GTFSR=Call_GTFSR()



# ---- SIDEBAR ----

st.sidebar.header("Please Filter Here:")

line = st.sidebar.multiselect(
    "Select the Luas Line:", 
    options=df_luas["Luas_Line"].unique(), 
    default="Green line",
    # key="lua_line_key"
)


tlist = st.sidebar.multiselect(
    "Select the Week of Year:",
    options=df_luas["T_LIST_LUA_Week"].unique(),
    default="2019W01",
    # key="tlist_lua_key"

)

bus_line = st.sidebar.multiselect(
    "Select the Mode of Transport:", 
    options=df_bus["Mode_of_Transport"].unique(), 
    default="Dublin Metro Bus",
    key="bus_line_key",
)


bus_tlist = st.sidebar.multiselect(
    "Select the Week of Year:",
    options=df_bus["T_LIST_BUS_Week"].unique(),
    default="2019W01",
    key="bus_tlist_key",
)

df_selection = df_luas.query("Luas_Line == @line & T_LIST_LUA_Week ==@tlist")
df_bus_selection = df_bus.query("Mode_of_Transport == @bus_line & T_LIST_BUS_Week ==@bus_tlist")


if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()  # This will halt the app from further execution.
# Check if the dataframe is empty:
if df_bus_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()  # This will halt the app from further execution

# Check if the dataframe is empty:


# ---- MAINPAGE ----
st.title(":station: Transport Data")
st.markdown("##")


passengers_by_week = (
    df_selection.groupby(by=["T_LIST_LUA_Week"])[["VALUE"]].sum().sort_values(by="VALUE")
)
# print(passengers_by_week.index)



tab1, tab2 = st.tabs(["**Luas**", "**Buses**"])
with tab1:
    fig_pass = px.histogram(
        passengers_by_week,
        x=passengers_by_week.index,
        y="VALUE",
        orientation="v",
        title="<b>Passengers by Week</b>",
        color_discrete_sequence=["#B6E880"] * len(passengers_by_week),
        template="plotly_white",
    )
    fig_pass.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))


    passengers_by_luas = (
        df_selection.groupby(by=["Luas_Line"])[["VALUE"]].sum().sort_values(by="VALUE")
    )
    # print(passengers_by_luas.index)
    fig_lua = px.histogram(
        passengers_by_luas,
        x=passengers_by_luas.index,
        y="VALUE",
        orientation="v",
        title="<b>Passengers by Lua</b>",
        color_discrete_sequence=["#636EFA"] * len(passengers_by_luas),
        template="plotly_white",
    )
    fig_lua.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))


    left_column, right_column = st.columns(2)
    left_column.plotly_chart(fig_lua, use_container_width=True)
    right_column.plotly_chart(fig_pass, use_container_width=True)
    cont = st.container()
    stops = cont.selectbox(
        "See the Stops:",
        options=stations_filters,
        key="stops",
        on_change=get_stop_details,
    )

    destination = cont.multiselect(
        "Select the Destination:", options=st.session_state.destination, key="destination"
    )


def get_data_gtfsr():
    
    
    with open('data.json', 'r') as json_file:
        dict_data = json.load(json_file)
        Entity=dict_data["entity"]
        id_list = list(map(parse_bus_payload, Entity))

        return id_list



with tab2:
    pass_bus_by_week = (
        df_bus_selection.groupby(by=["T_LIST_BUS_Week"])[["VALUE"]].sum().sort_values(by="VALUE")
    )
    fig_bus_pass = px.histogram(
        pass_bus_by_week,
        x=pass_bus_by_week.index,
        y="VALUE",
        orientation="v",
        title="<b>Passengers by Week</b>",
        color_discrete_sequence=["#19D3F3"] * len(pass_bus_by_week),
        template="plotly_white",
    )
    fig_bus_pass.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))


    passengers_by_bus = (
        df_bus_selection.groupby(by=["Mode_of_Transport"])[["VALUE"]].sum().sort_values(by="VALUE")
    )
    print(passengers_by_bus.index)
    fig_bus = px.histogram(
        passengers_by_bus,
        x=passengers_by_bus.index,
        y="VALUE",
        orientation="v",
        title="<b>Passengers by Bus</b>",
        color_discrete_sequence=["#FECB52"] * len(passengers_by_bus),
        template="plotly_white",
    )
    fig_bus.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))


    left_column, right_column = st.columns(2)
    left_column.plotly_chart(fig_bus, use_container_width=True)
    right_column.plotly_chart(fig_bus_pass, use_container_width=True)    

    bus_list1=get_data_gtfsr()
    bus_cont=st.container()
    bus_id=bus_cont.selectbox(
        "Select the Bus ID:",
        options=bus_list1,
        key="id",
        on_change=get_data_gtfsr,    
    )
    print(bus_id)
    BUS_ID=bus_id
    st.write("Trip Update for ",bus_id)
    with open('data.json', 'r') as json_file:
        dict_data = json.load(json_file)
    Entity=dict_data["entity"]

    bus_str = list(map(get_bus_status, Entity))
    
    bus_stop_details = bus_cont.multiselect(
        "See the Bus Stops:", options=st.session_state.bus_stops, key="bus_stops"
)


# ---- HIDE STREAMLIT STYLE ----
# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)
