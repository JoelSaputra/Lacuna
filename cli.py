from core.ingest import ingest
from core.load import load_folder
from core.retrieve import retrieve
from config import *
from google import genai
import os

def main():
    input_text = input("Enter your query: ")
    ingest(input_text)









