import streamlit as st

# Pages configuration
home_page = st.Page(page="projects/home.py", title="Home")
nlp_page = st.Page(page="projects/nlp.py", title="Natural Language Processing")
vision_page = st.Page(page="projects/vision.py", title="Computer Vision")
vision_example_page = st.Page(
    page="projects/vision_example.py", title="Computer Vision Example"
)
weather_page = st.Page(page="projects/weather.py", title="Weather")

pg = st.navigation(
    [
        home_page,
        nlp_page,
        vision_page,
        vision_example_page,
        weather_page,
    ]
)
pg.run()
