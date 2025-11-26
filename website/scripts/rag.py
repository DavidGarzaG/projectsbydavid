import boto3
from pydantic import BaseModel, validator

# This is all to create somewhat dynamic filters to search the Knowledge Base.
### This should probably live in other place. Here for now
region = "us-east-1"
bedrock = boto3.client("bedrock-runtime", region_name=region)
bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=region)

MODEL_ID = "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0"
kb_id = "DJ31JD5YCZ"
###


### Defining Pydantic models
# My Entity has Elevator in the Metadata.
class Entity(BaseModel):
    Elevator: str | None


# This is left as the original
class ExtractedEntities(BaseModel):
    entities: list[Entity]

    @validator("entities", pre=True)
    def remove_duplicates(cls, entities):
        unique_entities = []
        seen = set()
        for entity in entities:
            entity_tuple = tuple(sorted(entity.items()))
            if entity_tuple not in seen:
                seen.add(entity_tuple)
                unique_entities.append(dict(entity_tuple))
        return unique_entities


list_of_valid_filter_values = ["Elevador PVE 30", "Elevador PVE 37", "Elevador PVE 52"]


###
extracting_instructions = """
    The name of the elevator in spanish following this format: 'Elevador <model-name> <model-number>'.
    The 'E' in 'Elevador' is always uppercase.
    If pve is in the model name it goes uppercase as in 'PVE'.
    """

### Implement entity extraction using tool use
tools = [
    {
        "toolSpec": {
            "name": "extract_entities",
            "description": "Extract named entities from the text. If you are not 100% sure of the entity value, use 'unknown'.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "Elevator": {
                                        "type": "string",
                                        "description": extracting_instructions,
                                    },  #
                                },
                                "required": ["Elevator"],
                            },
                        }
                    },
                    "required": ["entities"],
                }
            },
        }
    }
]


def extract_entities(text):
    response = bedrock.converse(
        modelId=MODEL_ID,
        inferenceConfig={"temperature": 0, "maxTokens": 4000},
        toolConfig={"tools": tools},
        messages=[{"role": "user", "content": [{"text": text}]}],
    )

    json_entities = None
    for content in response["output"]["message"]["content"]:
        if "toolUse" in content and content["toolUse"]["name"] == "extract_entities":
            json_entities = content["toolUse"]["input"]
            break

    if json_entities:
        return ExtractedEntities.model_validate(json_entities)
    else:
        # print("No entities found in the response.")
        return None


### Construct a metadata filter
def construct_metadata_filter(extracted_entities):
    if not extracted_entities or not extracted_entities.entities:
        return None

    entity = extracted_entities.entities[0]
    metadata_filter = {"andAll": []}

    if entity.Elevator and entity.Elevator != "unknown":
        metadata_filter["andAll"].append(
            {"equals": {"key": "Elevator", "value": entity.Elevator}}
        )

    # If the filter is empty.
    if metadata_filter["andAll"] is []:
        return None

    # If there is only one filter, the filter goes without the andAll. I'll leave this here for now
    if len(metadata_filter["andAll"]) < 2:
        metadata_filter = metadata_filter["andAll"][0]

    # Assuring the filter is valid.
    if metadata_filter["equals"]["value"] not in list_of_valid_filter_values:
        metadata_filter = None

    return metadata_filter


### Create the main function
def process_query(text):
    extracted_entities = extract_entities(text)
    metadata_filter = construct_metadata_filter(extracted_entities)

    response = bedrock_agent_runtime.retrieve(
        knowledgeBaseId=kb_id,
        retrievalConfiguration={
            "vectorSearchConfiguration": {"filter": metadata_filter}
        },
        retrievalQuery={"text": text},
    )

    return response


def improving_query(text: str):
    """
    Helping the LLM a little bit.
    """
    if "pve" in text.lower():
        text = text.replace("pve", "PVE")

    return text
