import streamlit as st

# Pages configuration
home_page = st.Page(page="projects/home.py", title="Home")
vision_page = st.Page(page="projects/vision.py", title="Computer Vision")
nlp_page = st.Page(
    page="projects/nlp.py", title="(Coming Next!) Natural Language Processing"
)
weather_page = st.Page(page="projects/weather.py", title="(Coming Soon!) Weather")

pg = st.navigation(
    [
        home_page,
        vision_page,
        nlp_page,
        weather_page,
    ]
)
pg.run()
