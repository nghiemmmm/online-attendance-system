from pydantic_settings import BaseSettings
import streamlit as st
import os

class Settings(BaseSettings):
    API_URL: str
    # other secrets...

    class Config:
        env_file = ".env"

def load_settings():
    if "database" in st.secrets:  # running in Streamlit Cloud
        return Settings(API_URL=st.secrets["api"]["API_URL"])
    return Settings()  # fallback to env vars for local/dev/deploy

settings = load_settings()