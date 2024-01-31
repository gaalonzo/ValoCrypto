import streamlit as st
from streamlit_option_menu import option_menu
from web3 import Web3
from app import node_url, w3


if w3.is_connected():
    st.success("Connected to Ethereum node")
else:
    st.error("Failed to connect to Ethereum node")

account = st.text_input("Enter your Ethereum address:")
to_address = st.text_input("Enter recipient's Ethereum address:")

if to_address != "":

    if not w3.is_address(account) or not w3.is_address(to_address):
        st.error("Invalid Ethereum address")
        st.stop()

    amount = st.number_input("Amount (ETH):", min_value=0.0001, format="%.5f")
    if amount <= 0:
        st.error("Invalid transaction amount")
        st.stop()

st.header("Send ETH")

private_key = st.text_input("Enter your private key:", type="password")

if st.button("Send"):
    try:
        transaction = {
            'to': to_address,
            'value': w3.to_wei(amount, 'ether'),
            'gas': 200000,
            'gasPrice': w3.to_wei('50', 'gwei'),
            'nonce': w3.eth.get_transaction_count(account),
        }

        signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)

        transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

        st.success(f"Transaction sent! Transaction Hash: {transaction_hash.hex()}")
    except Exception as e:
        st.error(f"Error: {e}")
