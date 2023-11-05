import streamlit as st

import streamlit as st

# You can generate a button and perform the redirection if it's clicked
if st.button('Sida er flytta, trykk på meg for å komme til ny side.'):
    # Use Streamlit's function to render HTML
    st.markdown(
        '<meta http-equiv="refresh" content="0;url=https://geotoolz.streamlit.app/" />',
        unsafe_allow_html=True,
    )
