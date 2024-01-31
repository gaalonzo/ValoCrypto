import streamlit as st
import os
from web3 import Web3
import pandas as pd
import pickle
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
from statsmodels.tsa.arima.model import ARIMA
import time
from app import fetch_contract_data, timestamp_to_datetime


selected = option_menu(
    menu_title=None,
    options=["Ethereum Mainnet", "Sepolia", "Goerli"],
    icons=["currency-bitcoin", "envelope", "file-person-fill"],
    default_index=0,
    orientation="horizontal"
)

if selected == 'Ethereum Mainnet':
    selected = option_menu(
        menu_title=None,
        options=["INCHETH", "INCHUSD", "AAVEETH", "AAVEUSD", "ALCXETH", "AMPLETH", "AMPLUSD", "ANKRUSD"],
        default_index=0,
        orientation="horizontal"
    )

    if selected == "INCHETH":

        # Your existing setup
        mainweb3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x72AFAECF99C9d9C8215fF44C77B94B99C28741e8'
        contract = mainweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime

        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
        # Get the current timestamp and timestamp from 3 years ago

        def fetch_data_for_pair(contract_address):
            contract = mainweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Ethereum_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "INCHUSD":
        # Your existing setup
        mainweb3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0xc929ad75B72593967DE83E7F7Cda0493458261D9'
        contract = mainweb3.eth.contract(address=addr, abi=abi)

        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)


        def fetch_data_for_pair(contract_address):
            contract = mainweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Ethereum_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "AAVEETH":

            # Your existing setup
        mainweb3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x6Df09E975c830ECae5bd4eD9d90f3A95a4f88012'
        contract = mainweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = mainweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Ethereum_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "AAVEUSD":

            # Your existing setup
        mainweb3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x547a514d5e3769680Ce22B2361c10Ea13619e8a9'
        contract = mainweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = mainweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Ethereum_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "ALCXETH":

            # Your existing setup
        mainweb3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x194a9AaF2e0b67c35915cD01101585A33Fe25CAa'
        contract = mainweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = mainweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Ethereum_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "AMPLUSD":

            # Your existing setup
        mainweb3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0xe20CA8D7546932360e37E9D72c1a47334af57706'
        contract = mainweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = mainweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Ethereum_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "ANKRUSD":

            # Your existing setup
        mainweb3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x7eed379bf00005CfeD29feD4009669dE9Bcc21ce'
        contract = mainweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = mainweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Ethereum_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

elif selected == 'Sepolia':
    selected = option_menu(
        menu_title=None,
        options=["BTCETH", "BTCUSD", "CSPXUSD", "CZKUSD", "DAIUSD", "ETHUSD", "EURUSD", "FORTHUSD", "GBPUSD", "JPYUSD", "LINKETH", "LINKUSD", "SNXUSD", "USDCUSD", "XAUUSD"],
        default_index=0,
        orientation="horizontal"
    )

    if selected == "BTCETH":

            # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
            # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x5fb1616F78dA7aFC9FF79e0371741a747D2a7F22'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "BTCUSD":

            # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
            # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x1b44F3514812d835EB1BDB0acB33d3fA3351Ee43'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "CSPXUSD":


            # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
            # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x4b531A318B0e44B549F3b2f824721b3D0d51930A'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "CZKUSD":

            # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
            # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0xC32f0A9D70A34B9E7377C10FDAd88512596f61EA'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "DAIUSD":

            # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
            # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x14866185B1962B63C3Ea9E03Bc1da838bab34C19'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "ETHUSD":

            # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
            # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x694AA1769357215DE4FAC081bf1f309aDC325306'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago

        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "EURUSD":

            # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
            # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x1a81afB8146aeFfCFc5E50e8479e826E7D55b910'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "FORTHUSD":

            # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
            # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x070bF128E88A4520b3EfA65AB1e4Eb6F0F9E6632'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "GBPUSD":

            # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
            # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x91FAB41F5f3bE955963a986366edAcff1aaeaa83'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "JPYUSD":

            # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
            # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x8A6af2B75F23831ADc973ce6288e5329F63D86c6'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "LINKETH":

            # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
            # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x42585eD362B3f1BCa95c640FdFf35Ef899212734'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "SNXUSD":

        # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0xc0F82A46033b8BdBA4Bb0B0e28Bc2006F64355bC'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
        # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions


        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "USDCUSD":

        # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0xA2F78ab2355fe2f984D808B5CeE7FD0A93D5270E'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
        # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions


        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "XAUUSD":

        # Your existing setup
        sepweb3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0xC5981F461d74c46eB4b0CF3f4Ec79f025573B0Ea'
        contract = sepweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
        # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = sepweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df

        def train_and_predict_arima(data, pair):
            pickle_filename = f"Sepolia_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        last_date = df.index[-1]
        prediction_dates = [last_date + str(timedelta(days=i)) for i in range(1, 4)]
        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

elif selected == 'Goerli':
    selected = option_menu(
        menu_title=None,
        options=["BTCETH", "BTCUSD", "CZKUSD", "DAIUSD", "ETHUSD", "EURUSD", "FORTHUSD", "GBPUSD", "JPYUSD", "LINKETH", "LINKUSD", "SNXUSD", "USDCUSD", "XAUUSD"],
        default_index=0,
        orientation="horizontal"
    )
    if selected == "BTCETH":

        # Your existing setup
        goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x779877A7B0D9E8603169DdbD7836e478b4624789'
        contract = goerliweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
        # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = goerliweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Goerli_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions


        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "BTCUSD":

        # Your existing setup
        goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0xA39434A63A52E749F02807ae27335515BA4b07F7'
        contract = goerliweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
        # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = goerliweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Goerli_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions


        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "CZKUSD":

        # Your existing setup
        goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0xAE45DCb3eB59E27f05C170752B218C6174394Df8'
        contract = goerliweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
        # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = goerliweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Goerli_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions


        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "DAIUSD":

            # Your existing setup
            goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
            # AggregatorV3Interface ABI
            abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
            addr = '0x0d79df66BE487753B02D015Fb622DED7f0E9798d'
            contract = goerliweb3.eth.contract(address=addr, abi=abi)
            # Function to convert Unix timestamp to datetime
            def timestamp_to_datetime(timestamp):
                return datetime.utcfromtimestamp(timestamp)
            # Get the current timestamp and timestamp from 3 years ago
            def fetch_data_for_pair(contract_address):
                contract = goerliweb3.eth.contract(address=contract_address, abi=abi)

                # Fetch the latest round data
                latest_round_data = contract.functions.latestRoundData().call()
                latest_round_id = latest_round_data[0]

                # Iterate to fetch data
                round_data = []
                round_id = latest_round_id
                current_time = datetime.utcnow()
                three_years_ago = current_time - timedelta(days=1095)

                while True:
                    data = contract.functions.getRoundData(round_id).call()
                    round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                    if round_time < three_years_ago:
                        break

                    data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                    round_data.append(data_with_date)
                    round_id -= 1

                labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
                df = pd.DataFrame(round_data, columns=labels)
                df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
                df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
                df.set_index('date', inplace=True)

                return df


            def train_and_predict_arima(data, pair):
                pickle_filename = f"Goerli_{pair}_arima_model.pkl"

                # Check if a trained model exists
                if os.path.exists(pickle_filename):
                    with open(pickle_filename, 'rb') as file:
                        model_fit = pickle.load(file)
                else:
                    # Train the model if no saved model is found
                    model_ar = ARIMA(data, order=(1, 0, 0))
                    model_fit = model_ar.fit()
                    # Save the trained model
                    with open(pickle_filename, 'wb') as file:
                        pickle.dump(model_fit, file)

                # Predict the next 3 days
                predictions = model_fit.forecast(steps=3)
                return predictions


            pair = selected
            contract_address = addr

            df = fetch_data_for_pair(contract_address)
            df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
            df.dropna(subset=['answer'], inplace=True)

            # Integrate Streamlit spinner for ARIMA processing
            with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
                predictions = train_and_predict_arima(df['answer'].values, pair)
                time.sleep(5)  # Simulate a delay
            st.success('Predicción lograda!')

            # Create a new DataFrame for predicted values
            today = datetime.now()  # Get today's date
            prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

            prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
            st.write("Prediccion para los proximos 3 dias:")
            st.dataframe(prediction_df)


    elif selected == "ETHUSD":

        # Your existing setup
        goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0xD4a33860578De61DBAbDc8BFdb98FD742fA7028e'
        contract = goerliweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
        # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = goerliweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Goerli_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions


        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "EURUSD":

        # Your existing setup
        goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x44390589104C9164407A0E0562a9DBe6C24A0E05'
        contract = goerliweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
        # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = goerliweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Goerli_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions


        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "FORTHUSD":

        # Your existing setup
        goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x7A65Cf6C2ACE993f09231EC1Ea7363fb29C13f2F'
        contract = goerliweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
        # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = goerliweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Goerli_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions


        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "GBPUSD":


        # Your existing setup
        goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x73D9c953DaaB1c829D01E1FC0bd92e28ECfB66DB'
        contract = goerliweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)


        def fetch_data_for_pair(contract_address):
            contract = goerliweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Goerli_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions


        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "LINKETH":

        # Your existing setup
        goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0xb4c4a493AB6356497713A78FFA6c60FB53517c63'
        contract = goerliweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)


        def fetch_data_for_pair(contract_address):
            contract = goerliweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Goerli_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions


        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)


    elif selected == "LINKUSD":

        # Your existing setup
        goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x48731cF7e84dc94C5f84577882c14Be11a5B7456'
        contract = goerliweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)


        def fetch_data_for_pair(contract_address):
            contract = goerliweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Goerli_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions


        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "SNXUSD":

        # Your existing setup
        goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0xdC5f59e61e51b90264b38F0202156F07956E2577'
        contract = goerliweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)


        def fetch_data_for_pair(contract_address):
            contract = goerliweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Goerli_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions


        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "USDCUSD":

        # Your existing setup
        goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0xAb5c49580294Aff77670F839ea425f5b78ab3Ae7'
        contract = goerliweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)

        def fetch_data_for_pair(contract_address):
            contract = goerliweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Goerli_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions

        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)

    elif selected == "XAUUSD":

        # Your existing setup
        goerliweb3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/33a96136453d4323b36a158aa87d889a'))
        # AggregatorV3Interface ABI
        abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
        addr = '0x7b219F57a8e9C7303204Af681e9fA69d17ef626f'
        contract = goerliweb3.eth.contract(address=addr, abi=abi)
        # Function to convert Unix timestamp to datetime
        def timestamp_to_datetime(timestamp):
            return datetime.utcfromtimestamp(timestamp)
        # Get the current timestamp and timestamp from 3 years ago
        def fetch_data_for_pair(contract_address):
            contract = goerliweb3.eth.contract(address=contract_address, abi=abi)

            # Fetch the latest round data
            latest_round_data = contract.functions.latestRoundData().call()
            latest_round_id = latest_round_data[0]

            # Iterate to fetch data
            round_data = []
            round_id = latest_round_id
            current_time = datetime.utcnow()
            three_years_ago = current_time - timedelta(days=1095)

            while True:
                data = contract.functions.getRoundData(round_id).call()
                round_time = timestamp_to_datetime(data[3])  # 'updatedAt' timestamp

                if round_time < three_years_ago:
                    break

                data_with_date = list(data) + [round_time.strftime('%Y-%m-%d %H:%M:%S')]
                round_data.append(data_with_date)
                round_id -= 1

            labels = ["roundId", "answer", "startedAt", "updatedAt", "answeredInRound", "date"]
            df = pd.DataFrame(round_data, columns=labels)
            df['startedAt'] = pd.to_datetime(df['startedAt'], unit='s')
            df['updatedAt'] = pd.to_datetime(df['updatedAt'], unit='s')
            df.set_index('date', inplace=True)

            return df


        def train_and_predict_arima(data, pair):
            pickle_filename = f"Goerli_{pair}_arima_model.pkl"

            # Check if a trained model exists
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as file:
                    model_fit = pickle.load(file)
            else:
                # Train the model if no saved model is found
                model_ar = ARIMA(data, order=(1, 0, 0))
                model_fit = model_ar.fit()
                # Save the trained model
                with open(pickle_filename, 'wb') as file:
                    pickle.dump(model_fit, file)

            # Predict the next 3 days
            predictions = model_fit.forecast(steps=3)
            return predictions


        pair = selected
        contract_address = addr

        df = fetch_data_for_pair(contract_address)
        df['answer'] = pd.to_numeric(df['answer'], errors='coerce')
        df.dropna(subset=['answer'], inplace=True)

        # Integrate Streamlit spinner for ARIMA processing
        with st.spinner('Aplicando ARIMA para predecir los proximos 3 dias ...'):
            predictions = train_and_predict_arima(df['answer'].values, pair)
            time.sleep(5)  # Simulate a delay
        st.success('Predicción lograda!')

        # Create a new DataFrame for predicted values
        today = datetime.now()  # Get today's date
        prediction_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 4)]

        prediction_df = pd.DataFrame({'Fecha': prediction_dates, 'Prediccion': predictions})
        st.write("Prediccion para los proximos 3 dias:")
        st.dataframe(prediction_df)