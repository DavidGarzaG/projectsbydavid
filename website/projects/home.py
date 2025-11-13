import os

import streamlit as st

st.header("Welcome to Hire David!")

with st.container(border=True):
    st.write(
        """
        This website is a portfolio of some of my projects in different fields of Data Science.
        Each of the projects serves to demonstrate my skills and expertise."""
    )

st.subheader("Here is my latest Resume")
st.pdf(os.path.join(os.getcwd(), "website", "static", "Resume.pdf"), height=830)

st.image(os.path.join(os.getcwd(), "website", "static", "Brandy.JPG"), width=300)
