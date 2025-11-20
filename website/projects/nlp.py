import time

import boto3
import streamlit as st

st.title("RAG Pipeline Implementation")


client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
KNOWLEDGE_BASE_ID = "DJ31JD5YCZ"
model_arn = "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0"

# This is the predefined template (with slight modifications) that came with "Test Knowledge Base" in AWS.
# prompt_template = (
#     "You should always answer in the same language as the question.\n" # This is my only modification
#     "A chat between a curious User and an artificial intelligence Bot. The Bot gives helpful, detailed, and polite answers to the User's questions.\n"
#     "In this session, the model has access to set of search results and a user's question, your job is to answer the user's question using only information from the search results.\n"
#     "If the search results do not contain information that can answer the question, please respond with 'Sorry I could not find an exact answer to the question'.\n"
#     "Now, below is a list of texts retrieved for user's question. Read them carefully and then follow my instructions: \n"
#     "$search_results$\n\n"
#     "Using the information from above search results to provide answer to user's question.\n"
#     "Here is the user's query:\n"
#     "Question: $input$"
# )

prompt_template = (
    "Use the following retrieved elevator specs to answer the question. You should always answer in the same language as the question.\n"
    "Specs:\n"
    "$search_results$\n\n"
    "Question: $input$"
)


def retrieve_and_generate(query, model_arn, top_k=5, prompt_template=None):
    # prompt_template is optional, you could pass your own prompt design
    request_body = {
        "input": {"text": query},
        "retrieveAndGenerateConfiguration": {
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                "modelArn": model_arn,
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {"numberOfResults": top_k}
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
                prompt, model_arn=model_arn, top_k=5, prompt_template=prompt_template
            )
        )

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
