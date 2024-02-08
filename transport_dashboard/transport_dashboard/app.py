import pandas as pd
import plotly.express as px
import streamlit as st
import luas.api
from luas.api import LuasLine, LuasDirection
import json


luas_client = luas.api.LuasClient()

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


def int_try_parse(value):
    try:
        int(value)
        return True
    except:
        return False


# ---- READ EXCEL ----
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io="Passenger Journeys by Luas.xlsx",
        engine="openpyxl",
        sheet_name="Unpivoted",
        # skiprows=3,
        usecols="C:H",
        nrows=793,
    )

    return df


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


df = get_data_from_excel()

# ---- SIDEBAR ----

st.sidebar.header("Please Filter Here:")

line = st.sidebar.multiselect(
    "Select the Luas Line:", options=df["Luas_Line"].unique(), default="Green line"
)


tlist = st.sidebar.multiselect(
    "Select the T_LIST_Week:",
    options=df["T_LIST_Week"].unique(),
    default="2019W01",
)


df_selection = df.query("Luas_Line == @line & T_LIST_Week ==@tlist")

# Check if the dataframe is empty:
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()  # This will halt the app from further execution.

# ---- MAINPAGE ----
st.title(":station: Transport Data")
st.markdown("##")


passengers_by_week = (
    df_selection.groupby(by=["T_LIST_Week"])[["VALUE"]].sum().sort_values(by="VALUE")
)
# print(passengers_by_week.index)
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
    "Select the Stops:",
    options=stations_filters,
    key="stops",
    on_change=get_stop_details,
)
destination = cont.multiselect(
    "Select the Destination:", options=st.session_state.destination, key="destination"
)
# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
