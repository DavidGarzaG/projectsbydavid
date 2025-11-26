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
    "If you do not find the information required ask for clarification of the question."
    "Do not give information if you do not have textual information about it."
    "If available, give the name of the document from where you get the information."
    "Specs:\n"
    "$search_results$\n\n"
    "Question: $input$"
)


def retrieve_and_generate(query, model_arn, top_k=6, prompt_template=None):
    query = improving_query(query)

    # Adding a filter.
    extracted_entities = extract_entities(query)
    metadata_filter = construct_metadata_filter(extracted_entities)

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
                    }
                },
            },
        },
    }

    # Add previous metadata_filter if it is None.
    if metadata_filter is None and "metadata_filter" in st.session_state:
        metadata_filter = st.session_state["metadata_filter"]

    # Add the metadata_filter to the request body if there is one.
    if metadata_filter is not None:
        request_body["retrieveAndGenerateConfiguration"]["knowledgeBaseConfiguration"][
            "retrievalConfiguration"
        ]["vectorSearchConfiguration"]["filter"] = metadata_filter
        st.session_state["metadata_filter"] = metadata_filter

    # If you have a custom prompt template
    if prompt_template is not None:
        request_body["retrieveAndGenerateConfiguration"]["knowledgeBaseConfiguration"][
            "generationConfiguration"
        ] = {"promptTemplate": {"textPromptTemplate": prompt_template}}

    # If there is session id
    if "session_id" in st.session_state:
        request_body["sessionId"] = st.session_state["session_id"]

    # Make the call to the LLM
    response = client.retrieve_and_generate(**request_body)

    # Store the session Id for the interaction.
    st.session_state["session_id"] = response["sessionId"]

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
