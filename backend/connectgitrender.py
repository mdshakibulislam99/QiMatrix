from fastapi.middleware.cors import CORSMiddleware
# This imports the 'app' object from your main_new.py file
from main_new import app 

# This allows your GitHub website to talk to this Render server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
