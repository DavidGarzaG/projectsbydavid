import time

import boto3
import streamlit as st

from website.scripts.rag import (
    construct_metadata_filter,
    extract_entities,
    improving_query,
)

st.title("RAG Pipeline Implementation")


client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
KNOWLEDGE_BASE_ID = "DJ31JD5YCZ"
model_arn = "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0"

prompt_template = (
    "Use the following retrieved elevator specs to answer the question. You should always answer in the same language as the question.\n"
    "Specs:\n"
    "$search_results$\n\n"
    "Question: $input$"
)


def retrieve_and_generate(query, model_arn, top_k=6, prompt_template=None):
    query = improving_query(query)

    # Adding a filter.
    extracted_entities = extract_entities(query)
    metadata_filter = construct_metadata_filter(extracted_entities)

    # If there is only have one filter, the filter goes without the andAll. I'll leave this here for now
    if len(metadata_filter["andAll"]) < 2:
        metadata_filter = metadata_filter["andAll"][0]

    # prompt_template is optional, you could pass your own prompt design
    request_body = {
        "input": {"text": query},
        "retrieveAndGenerateConfiguration": {
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                "modelArn": model_arn,
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {
                        "numberOfResults": top_k,
                        "filter": metadata_filter,
                    }
                },
            },
        },
    }

    # If you have a custom prompt template
    if prompt_template is not None:
        request_body["retrieveAndGenerateConfiguration"]["knowledgeBaseConfiguration"][
            "generationConfiguration"
        ] = {"promptTemplate": {"textPromptTemplate": prompt_template}}

    response = client.retrieve_and_generate(**request_body)

    for word in response["output"]["text"].split():
        yield word + " "
        time.sleep(0.05)


with st.container(border=True):
    st.write(
        """
        Here is a small chatbot implementation.\n
        It answers in **spanish** regarding information about three specific elevator models:
        PVE 30, PVE 37 and PVE 52."""
    )

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("¿Que quieres saber de Eco Elevadores?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(
            retrieve_and_generate(
                prompt, model_arn=model_arn, top_k=6, prompt_template=prompt_template
            )
        )

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
