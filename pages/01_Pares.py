import streamlit as st
from streamlit_option_menu import option_menu
from web3 import Web3
import pandas as pd
from datetime import datetime, timedelta
import time
from app import fetch_contract_data, timestamp_to_datetime


selected = option_menu(
    menu_title=None,
    options=["Ethereum Mainnet", "Sepolia", "Goerli"],
    icons=["currency-bitcoin", "envelope", "file-person-fill"],
    default_index=0,
    orientation="horizontal"
)

# Ethereum Mainnet pairs
ethmain_pairs_dict = {
    "INCHETH": '0x72AFAECF99C9d9C8215fF44C77B94B99C28741e8',
    "INCHUSD": '0xc929ad75B72593967DE83E7F7Cda0493458261D9',
    "AAVEETH": '0x6Df09E975c830ECae5bd4eD9d90f3A95a4f88012',
    "AAVEUSD": '0x547a514d5e3769680Ce22B2361c10Ea13619e8a9',
    "ALCXETH": '0x194a9AaF2e0b67c35915cD01101585A33Fe25CAa',
    "AMPLETH": '0x492575FDD11a0fCf2C6C719867890a7648d526eB',
    "AMPLUSD": '0xe20CA8D7546932360e37E9D72c1a47334af57706',
    "ANKRUSD": '0x7eed379bf00005CfeD29feD4009669dE9Bcc21ce'
}
# Web3 setup
mainweb3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
# AggregatorV3Interface ABI
abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
# Labels for the data
labels = ["Pair", "roundId", "answer", "startedAt", "updatedAt", "answeredInRound"]
# List to hold all data
all_data = []
# Fetch the latest round data for each pair
for pair, address in ethmain_pairs_dict.items():
    # Set up contract instance
    contract = mainweb3.eth.contract(address=address, abi=abi)
    # Fetch the latest round data
    latestRoundData = contract.functions.latestRoundData().call()
    # Add pair name to the data
    data = [pair] + list(latestRoundData)
    data[3] = timestamp_to_datetime(data[3])  # Convert startedAt
    data[4] = timestamp_to_datetime(data[4])  # Convert updatedAt
    all_data.append(data)
# Create DataFrame
df = pd.DataFrame(all_data, columns=labels)

sep_pairs_dict = {
    "BTCETH" : '0x5fb1616F78dA7aFC9FF79e0371741a747D2a7F22',
    "BTCUSD" : '0x1b44F3514812d835EB1BDB0acB33d3fA3351Ee43',
    "CSPXUSD" : '0x4b531A318B0e44B549F3b2f824721b3D0d51930A',
    "CZKUSD" : '0xC32f0A9D70A34B9E7377C10FDAd88512596f61EA',
    "DAIUSD" : '0x14866185B1962B63C3Ea9E03Bc1da838bab34C19',
    "ETHUSD" : '0x694AA1769357215DE4FAC081bf1f309aDC325306',
    "EURUSD" : '0x1a81afB8146aeFfCFc5E50e8479e826E7D55b910',
    "FORTHUSD" : '0x070bF128E88A4520b3EfA65AB1e4Eb6F0F9E6632',
    "GBPUSD" : '0x91FAB41F5f3bE955963a986366edAcff1aaeaa83',
    "GHOUSD" : '0x635A86F9fdD16Ff09A0701C305D3a845F1758b8E',
    "IB01USD" : '0xB677bfBc9B09a3469695f40477d05bc9BcB15F50',
    "IBTAUSD" : '0x5c13b249846540F81c093Bc342b5d963a7518145',
    "JPYUSD" : '0x8A6af2B75F23831ADc973ce6288e5329F63D86c6',
    "LINKETH" : '0x42585eD362B3f1BCa95c640FdFf35Ef899212734',
    "LINKUSD" : '0xc59E3633BAAC79493d908e63626716e204A45EdF',
    "SNXUSD" : '0xc0F82A46033b8BdBA4Bb0B0e28Bc2006F64355bC',
    "USDCUSD" : '0xA2F78ab2355fe2f984D808B5CeE7FD0A93D5270E',
    "XAUUSD" : '0xC5981F461d74c46eB4b0CF3f4Ec79f025573B0Ea'
}

# Web3 setup
sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
# AggregatorV3Interface ABI
abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
# Labels for the data
labels = ["Pair", "roundId", "answer", "startedAt", "updatedAt", "answeredInRound"]
# List to hold all data
all_data = []

# Fetch the latest round data for each pair
for pair, address in sep_pairs_dict.items():
    # Set up contract instance
    contract = sepweb3.eth.contract(address=address, abi=abi)
    # Fetch the latest round data
    latestRoundData = contract.functions.latestRoundData().call()
    # Add pair name to the data
    data = [pair] + list(latestRoundData)
    data[3] = timestamp_to_datetime(data[3])  # Convert startedAt
    data[4] = timestamp_to_datetime(data[4])  # Convert updatedAt
    all_data.append(data)
# Create DataFrame
df2 = pd.DataFrame(all_data, columns=labels)


goerli_pairs_dict = {
    "BTCETH" : '0x779877A7B0D9E8603169DdbD7836e478b4624789',
    "BTCUSD" : '0xA39434A63A52E749F02807ae27335515BA4b07F7',
    "CZKUSD" : '0xAE45DCb3eB59E27f05C170752B218C6174394Df8',
    "DAIUSD" : '0x0d79df66BE487753B02D015Fb622DED7f0E9798d',
    "ETHUSD" : '0xD4a33860578De61DBAbDc8BFdb98FD742fA7028e',
    "EURUSD" : '0x44390589104C9164407A0E0562a9DBe6C24A0E05',
    "FORTHUSD" : '0x7A65Cf6C2ACE993f09231EC1Ea7363fb29C13f2F',
    "GBPUSD" : '0x73D9c953DaaB1c829D01E1FC0bd92e28ECfB66DB',
    "JPYUSD" : '0x982B232303af1EFfB49939b81AD6866B2E4eeD0B',
    "LINKETH" : '0xb4c4a493AB6356497713A78FFA6c60FB53517c63',
    "LINKUSD" : '0x48731cF7e84dc94C5f84577882c14Be11a5B7456',
    "SNXUSD" : '0xdC5f59e61e51b90264b38F0202156F07956E2577',
    "USDCUSD" : '0xAb5c49580294Aff77670F839ea425f5b78ab3Ae7',
    "XAUUSD" : '0x7b219F57a8e9C7303204Af681e9fA69d17ef626f'
}
goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))

# AggregatorV3Interface ABI
abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

# Labels for the data
labels = ["Pair", "roundId", "answer", "startedAt", "updatedAt", "answeredInRound"]
# List to hold all data
all_data = []

# Fetch the latest round data for each pair
for pair, address in goerli_pairs_dict.items():
    # Set up contract instance
    contract = goerliweb3.eth.contract(address=address, abi=abi)
    # Fetch the latest round data
    latestRoundData = contract.functions.latestRoundData().call()
    # Add pair name to the data
    data = [pair] + list(latestRoundData)
    data[3] = timestamp_to_datetime(data[3])  # Convert startedAt
    data[4] = timestamp_to_datetime(data[4])  # Convert updatedAt
    all_data.append(data)
# Create DataFrame
df3 = pd.DataFrame(all_data, columns=labels)


if selected == 'Ethereum Mainnet':
        df = fetch_contract_data(mainweb3, ethmain_pairs_dict, abi)
        st.title('Ethereum Mainnet Data')
        st.dataframe(df)
elif selected == 'Sepolia':
        df2 = fetch_contract_data(sepweb3, sep_pairs_dict, abi)
        st.title('Sepolia Data')
        st.dataframe(df2)
elif selected == 'Goerli':
        df3 = fetch_contract_data(goerliweb3, goerli_pairs_dict, abi)
        st.title('Goerli Data')
        st.dataframe(df3)
