import streamlit as st

# Insert JavaScript in the app to redirect immediately
st.markdown(
    '<script>window.location.href = "https://geotoolz.streamlit.app/Skredvær";</script>',
    unsafe_allow_html=True,
)
