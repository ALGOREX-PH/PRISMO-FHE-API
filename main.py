from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import requests
from fastapi.middleware.cors import CORSMiddleware
# Initialize FastAPI app
app = FastAPI()

# Set your OpenAI API key

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a request body model
class ChatRequest(BaseModel):
    api_key: str
    message: str

class checkRequest(BaseModel) :
    api_key: str
    question: str
    explanation_criteria: str
    correct_answer: str
    student_final_answer: str
    student_final_answer_explantation : str

class transcribeRequest(BaseModel) :
    api_key: str
    url : str

# Define a route for the chatbot
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        openai.api_key = request.api_key
        # Call OpenAI API to get the response
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Use the appropriate model name
            messages=[{"role": "user", "content": request.message}],
            max_tokens=150,
            temperature=0.7
        )
        answer = response.choices[0].message["content"]
        return {"response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# /transcribe Endpoint
@app.post("/transcribe")
async def transcribe (request: transcribeRequest) :
    try :
        openai.api_key = request.api_key
        # URL of the audio file
        url = "https://ff4679187d7d6e722749220544c0294968c31ebe81993eccedfa143-apidata.googleusercontent.com/download/storage/v1/b/dev-certai-audio-answers/o/answers%2Fquestion_1_1731300188824.wav?jk=AXvcXDt00Chw_X174DWb0aQ7ZEVtyp3_Qe6yZu1VuXttbRIQfB7CIhhBjzKskilHkF09Rg5nGGpkx2949wGQuxw12VIn5Oqk6Be-rSBCi_S5QLFnBIo60tl8Qe7XHdO2sFmKzziNGtnAaTH4bVPzCu61_aCZPWIt61aHbLwrD5d65YgCqiLW9u6FpYssCc2dH3kX8DIjB8kx7PsvA2uVt-xyayt9uJOdZGMD6jVowG158gf5BD_karRMMRYTKVeT5iJY6pODBN1khdV6XlUCsH9fkEmjOp-2IE4r55pkGYQHdnFn_XlEbfNgrIGLrIJP1nC3NJ_fl0_mSdgYf8Tt8815pCClb9fFf2oBBHznjUvm4BIwjxc4lw6P9xUsqXQPArHNzPUm6laqOY9Adr1RYJu2J69oD08R85iSHKoMI0S_Wn6aZAvANXs5rhEtnNlGNQvJgq4k5dL1H2SiOX6AzQQjaqWBn-PgGxFx1KBkkvyoGNvPSaWOBM3Fg-ewmuU0tIz9T3em-rfSu-ZLPzJfvjOi8a5Czfl85XFU7jmsP2MOhfs5Kac0XEQJSMMMt5gY_ZSYzax45AtRRFVTdT2IjPNTi2s_d0iCxKjleU3cyWBE02aDGKDcBzoaVtT5AnBFBkXFTH131BvJvg3IakMcOd9iztAa1vDT6NNxULVjlsMlq0O0-4zah59cCtXmcviSqFb_vb2RWy5IcyOjuyKGNQ_Qjxgtep24EminVfrJc8HB9rAE4-kRcZybFqvVm-Mo_6g5kwgef2coL6SPCkjGRbyp3VDoZAE2ohvCZJFTYjYIjnkZ01s3NHfCERukWYqZcSHZOTEHh1LzPSqstHM3UfQM-1sp5f3a3f3r50ucxgIisGmEl0FBlbjbSf3TdzjRJYUbEPApDtbrZygZpHXsvsL4SPvLNPIuI-0UMKjQTZhPJMBgSPWEtdbqUFKfagSQ74tBxwBUnm6n4K9PQ6tsiRGWp5QakfsWJqaz8sH9mDWDYC4ssBKXWMZgpmZceNMDEGDnGSQgkZfkcoswn0z49OcIbvLzh3CztXVi0jMYEW4RgG-CH53HGmZUj74quF3tI16gNtm484eRQ8RPfaU4zezSuazyn7n_G98GBZ4ZYHTGp1Y9arGwN8xeP8HA3VG_E7g-oB9FphRBqLas9DAwu1ocP-xg90TvjtCjXOzd_IOaKFHheICtdgth2PCBHcX9lB01s-F59tQQrF5hX5cvPDYDCaAPiGpIJXBvRj7uxYkDmEHe02EC3pOxgzu-C15rHMCKzz_2S2Nk&isca=1"

        # Send a GET request to the URL
        response = requests.get(url)

        # Save the content to a local file if the request was successful
        if response.status_code == 200:
           with open("question_1.wav", "wb") as f:
                f.write(response.content)
        else:
           return {"Transcription": "Cant open audio"}
        
        audio_file= open("question_1.wav", "rb")
        transcription = openai.Audio.transcribe(model="whisper-1", file=audio_file)
        return {"Transcription": transcription.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check")
async def check (request: checkRequest) :
    try:
        openai.api_key = request.api_key
        System_Prompt = """
You are an ai assistant that will take in a multiple choice questions alongside the user's final answer and explanation.

The User's answer needs to provide the final answer alongside their explanation on why that is the answer. The grading of each question must be 0.7 for the final answer and 0.3 for the explanation. If the User is wrong, the ai will provide the correct answer and explanation on why it is the correct answer. Else if the user is correct, the AI will acknowledge it accordingly. The AI will evaluate the user's answer and provide the user with feedback.


To Score the Explanation of the User per question, you will be providing a general criteria in which will grant the user 0.1 of the 0.3 points for explanation if they are able to achieve atleast one of it.

General Criteria :
Accuracy of Information: The explanation should accurately reflect established knowledge about AI and machine learning, specifically regarding prompt engineering.

Clarity of Explanation: The explanation should be clear and understandable, avoiding technical jargon where possible or defining such terms when used.

Relevance to the Question: Ensure that the explanation directly addresses the question asked, linking back to the specific techniques or concepts referenced in the question.

Depth of Insight: Look for explanations that provide depth beyond a superficial understanding, indicating critical thinking or application of the concept.

Evidence of Practical Understanding: Favor explanations that include practical examples or real-world applications of the concept, demonstrating how it can be applied outside theoretical contexts.

Then for the 0.2 points of the 0.3 Points for explanation will be coming from the provided Explanation Criteria in the context for each question. A user who atleast fulfills one explanation criteria will be granted 0.1 points, while a user who fulfills atleast two explanation criteria will be granted 0.2 points.
""" + request.question + " \n Explanation Criteria : \n" + request.explanation_criteria + "\n" + "Correct Answer : " + request.correct_answer
        struct = [ {"role": "system", "content": System_Prompt} ]
        user_answer = "User Final Answer : " + request.student_final_answer + "\n Explanation : " + request.student_final_answer_explantation
        struct.append({"role" : "user", "content" : user_answer})
        openai.api_key = request.api_key
        response = openai.ChatCompletion.create(model="gpt-4o-mini", messages = struct, temperature=0.2, max_tokens=3500, top_p=1, frequency_penalty=0, presence_penalty=0)
        answer = response.choices[0].message.content
        return {"response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint for testing
@app.get("/")
async def root():
    return {"message": "Welcome to Generative Labs's CertAI API!"}