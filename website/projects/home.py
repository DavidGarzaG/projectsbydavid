import os

import streamlit as st

st.header("Welcome to ProjectsByDavid!")

with st.container(border=True):
    st.write(
        """
        This website is a portfolio of some projects in different fields of Data Science.
        Each of the projects serves to demonstrate my skills and expertise in managing an end to end product.\\
        \\
        In some sense, the actual website currently running in AWS is the first project that you can observe.
    """
    )

st.markdown(
    """
    ## How does the website work?
    This website runs with **Python** code written and saved into a **git respository**, which can be viewed here on [Github](https://github.com/DavidGarzaG/projectsbydavid).
    This code is containerized using **Docker** and the image is stored both in [Docker Hub](https://hub.docker.com/r/packe/projectsbydavid) and in **Amazon's Elastic Container Registry** (ECR).
    This Docker Image is then pulled by **Amazon's Elastic Container Service** (ECS) which has a **Cluster** running with a **Task Definition** of the
    latest version of the website. To access the website the domain was registered using **Amazon's Route 53**, which in place routes any incoming traffic to an
    **Application Load Balancer** which is connected to the **ECS Cluster** that runs the task. Every service in the Amazon Web Services listed is connected with a
    **Virtual Private Cloud** (VPC) which hosts different artifacts such as **Listeners**, **Security Groups** and **Target Groups** that create this web application.
"""
)

st.subheader("Here is my latest Resume")
st.pdf(os.path.join(os.getcwd(), "website", "static", "Resume.pdf"), height=830)

# # This is Brandy
# st.image(os.path.join(os.getcwd(), "website", "static", "Brandy.JPG"), width=300)
