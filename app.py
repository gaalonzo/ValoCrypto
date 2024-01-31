import pickle
from pathlib import Path
import streamlit as st
import requests
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from web3 import Web3
import pandas as pd
from datetime import datetime, timedelta
import time

node_url = 'https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'


st.set_page_config(page_title="Valo Crypto", page_icon=":chart_with_downwards_trend:", layout="wide", menu_items={
    'About':"# This is a prototype app for Ethereum users",
})


def timestamp_to_datetime(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def fetch_contract_data(web3, pairs_dict, abi):
    labels = ["Pair", "roundId", "answer", "startedAt", "updatedAt", "answeredInRound"]
    all_data = []

    for pair, address in pairs_dict.items():
        contract = web3.eth.contract(address=address, abi=abi)
        latestRoundData = contract.functions.latestRoundData().call()
        data = [pair] + [str(item) for item in latestRoundData]  # Convert all data to strings
        data[3] = timestamp_to_datetime(int(data[3]))  # Convert startedAt
        data[4] = timestamp_to_datetime(int(data[4]))  # Convert updatedAt
        all_data.append(data)

    return pd.DataFrame(all_data, columns=labels)

def safe_int_conversion(value):
    try:
        # Attempt to convert to a Python int, if possible
        return int(value)
    except OverflowError:
        # If the value is too large, handle it as a string
        return str(value)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_hello = load_lottieurl("https://lottie.host/1e3a0a44-a796-4f74-9ccb-66f0bc63d771/ooL52FglIV.json")

w3 = Web3(Web3.HTTPProvider(node_url))


with st.container():
    left_column, right_column = st.columns(2)
    with left_column:
        #Una vez que tengamos logo
        #image = Image.open('Vesta.png')
        #nuevologo = image.resize((73, 86))
        #st.image(nuevologo)

        st.subheader("Welcome to Valo Crypto")
        st.title("Crypto DeFi" + " "+ " " + ":chart_with_upwards_trend:")
        st.write("This is a helpful tool to learn more about our incomes, our expenses, predict our weekly Crypto Transactions.")


    with right_column:
        st_lottie(
            lottie_hello,
            speed=1,
            reverse = False,
            loop= True,
            quality="low",
            height = 300,
            width=None,
            key=None
        )
        
        

#############################################################

