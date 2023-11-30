
#-----------------------------------------CHATBOT MODULE----------------------------------------------------

import speech_recognition as sr
import os
import pyaudio
import wave
import pyttsx3
from gtts import gTTS
import pygame
import pandas as pd
import os
import openai
import docx
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from supporting_modul import initialize_dataframes, context, chatbot, output_files


##############
#   API Key  #
##############

load_dotenv()
openai.api_key=os.getenv("OPENAI_KEY")

###############################
#    Paths to the databases   #
###############################

existing_customers_xls_path=r"C:\Users\vbanai\Documents\Programming\Dezsi porject\Chatbot02\tesztexcel.xlsx"
potential_customers_xls_path=r"C:\Users\vbanai\Documents\Programming\Dezsi porject\Chatbot02\tesztexcel_general.xlsx"
general_services_file_path = r"C:\Users\vbanai\Documents\Programming\Dezsi porject\Chatbot02\Vásárolható_autók.docx"
voice_path=r"C:\Users\vbanai\Documents\Programming\Dezsi porject\ChatBot02\WELCOME_BYASSISTANT.mp3"

##########################
#   ChatBot functions    #
##########################

df_existing_customer_original, df_existing_customer, df_potential_customer, word_text = initialize_dataframes(existing_customers_xls_path, potential_customers_xls_path, general_services_file_path)
context=context(df_existing_customer, word_text)
chatbot(context, voice_path)
output_files(context, df_existing_customer_original, df_existing_customer, df_potential_customer, existing_customers_xls_path, potential_customers_xls_path)

#------------------------------------------------------------------------------------------------