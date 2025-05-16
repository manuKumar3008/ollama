# Import necessary libraries
from fastapi import FastAPI, HTTPException                    # FastAPI for building the API, HTTPException for error handling
from fastapi.middleware.cors import CORSMiddleware            # CORS middleware to allow requests from other domains
from pydantic import BaseModel                                # For request body validation
import nest_asyncio                                           # To allow nested event loops (important in Jupyter or environments with running loops)
import uvicorn                                                # To serve the FastAPI app
import ollama                                                 # Assuming Ollama is an installed library for handling model chat generation

# Create a FastAPI instance
app = FastAPI()

# OPTIONAL: Enable CORS (Cross-Origin Resource Sharing) if frontend and backend are on different origins
# Uncomment and configure as needed
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],            # In production, set this to your frontend domain
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Define a Pydantic model for the incoming request body
class PromptRequest(BaseModel):
    prompt: str                      # The user input prompt for text generation
    # max_length: int = 50           # Optional: you could add more fields for model customization


# Function to handle the chat generation via Ollama
def stream_chat(prompt, model='llama3.2'):
    """
    Sends the user's prompt to the Ollama model and retrieves a response.
    """
    response = ollama.chat(
        model=model,
        messages=[
            {'role': 'user', 'content': prompt}
        ],
    )
       
    return response.message.content


# Define a POST endpoint to handle text generation
@app.post("/generate/")
async def generate_text(request: PromptRequest):
    """
    Receives a prompt and returns a model-generated response.
    """
    try:
        # Call the model with the user's prompt
        response = stream_chat(request.prompt)
        print(response)  # For debugging/logging purposes

        # Return the model's response
        return {"response": response}

    except Exception as e:
        # Return 500 error if something goes wrong
        raise HTTPException(status_code=500, detail=str(e))


# Apply nest_asyncio to allow uvicorn to run in notebooks or nested loops
nest_asyncio.apply()

# Run the FastAPI app using Uvicorn
uvicorn.run(app)
