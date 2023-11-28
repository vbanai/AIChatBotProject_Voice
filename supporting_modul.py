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

#-----------------------------------------------------------------------------------------------
#                 Reading the databases needed for the process in
#-----------------------------------------------------------------------------------------------
def initialize_dataframes(existing_customers_xls_path, potential_customers_xls_path, general_services_file_path):
  df_existing_customer_original=pd.read_excel(existing_customers_xls_path)
  df_existing_customer=df_existing_customer_original.to_string(index=False)
  df_potential_customer=pd.read_excel(potential_customers_xls_path)

  doc=docx.Document(general_services_file_path)
  full_text=""
  for paragraph in doc.paragraphs:
    full_text+=paragraph.text+ "\n"
  word_text=full_text.strip()

  return df_existing_customer_original, df_existing_customer, df_potential_customer, word_text


#-----------------------------------------------------------------------------------------------
#                   Message generator
#-----------------------------------------------------------------------------------------------

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
  response = openai.ChatCompletion.create(
      model=model,
      messages=messages,
      temperature=temperature, 
  )
  return response.choices[0].message["content"]

#-----------------------------------------------------------------------------------------------
#                    Promt 
#-----------------------------------------------------------------------------------------------

def context(df_existing_customer, word_text):
  context = [
    {'role': 'system', 'content': f"""
    You are telefonoperator in AutoDé Kft and you are answering incoming questions in Hungarian.\
    First generate the following sentence: "Üdvözöllek, Zsuzsanna vagyok, kérlek mondd el miben segíthetek". \
    If the user has question regarding the ongoing order, ask the client number.\
    If the user has general questions don't need to ask the client number \            
    User: Can you give me the client number? Assistant: Please give me your client number.\
    If the client number is provided, answer to the user according to  the table:{df_existing_customer} \
    Without the client number, start chatting with the user, you can't use external sources, only the 
    document:{word_text}. \
    Respond briefly (max 10 words), always ask if you can help with anything else. 
    
  """}]
  return context

#-----------------------------------------------------------------------------------------------
#                      CHAT BOT - Production
#-----------------------------------------------------------------------------------------------
def chatbot(context, file_path):
  r = sr.Recognizer()
  while True:
    with sr.Microphone() as source2:
      r.adjust_for_ambient_noise(source2, duration=3)
      
      #1.) TEXT TO AUDIO (the chatbot assistant says a welcome message loud)
      #  Chatbot says: Hello I am Sue, how can I help you?
      
      response=get_completion_from_messages(context) 
      context.append({'role':'assistant', 'content':f"{response}"})
      
      tts = gTTS(response, lang='hu')
      tts.save(file_path)
      file_path =file_path
      pygame.init()
      pygame.mixer.init()
      pygame.mixer.music.load(file_path)
      pygame.mixer.music.play()
      clock = pygame.time.Clock()
      while pygame.mixer.music.get_busy():
          clock.tick(10) 
      pygame.mixer.music.stop()
      pygame.quit()

      #2.) Listening to the client's reply:

      try:

          audio2=r.listen(source2, timeout=10)
          promt=r.recognize_google(audio2, language="hu-HU")
          context.append({'role':'user', 'content':f"{promt}"})
    
      except Exception as e:
          break

#-----------------------------------------------------------------------------------------------
#             Updating the databases with the new conversation
#-----------------------------------------------------------------------------------------------

def output_files(context, df_existing_customer_original, df_existing_customer, df_potential_customer, existing_customers_xls_path, potential_customers_xls_path):
  text=""
  for i in context:
    if i['role']=='assistant' or i['role']=='user':
      text+=(i['role'].capitalize()+ " : " +i['content']+ " | ")

  current_date = datetime.now().date()
  current_date = current_date.strftime("%Y-%m-%d")
  new_column_header = 'Chat'+ current_date

  spotting_identifier=df_existing_customer_original["Azonosító"].apply(lambda x: text.lower().find(str(x).lower()) !=-1)

  if not any(spotting_identifier)==True:
    if new_column_header not in df_potential_customer.columns.tolist():
      df_potential_customer[new_column_header]=None
      df_potential_customer.loc[2, new_column_header]=''
      df_potential_customer.loc[2, new_column_header]+=text
      df_potential_customer.to_excel(potential_customers_xls_path, index=False)
    else:
      last_not_empty_index=df_potential_customer[new_column_header].last_valid_index()
      df_potential_customer.loc[last_not_empty_index+1, new_column_header]=''
      df_potential_customer.loc[last_not_empty_index+1, new_column_header]+=text
      df_potential_customer.to_excel(potential_customers_xls_path, index=False)
    
  else:
    if new_column_header not in df_existing_customer_original.columns.tolist():
      df_existing_customer_original[new_column_header]=''

    else:


      row=df_existing_customer_original[spotting_identifier].index.item()
      # if df.loc[row, new_column_header] is None:
      #     df.loc[row, new_column_header] = df[row, new_column_header].astype(str)


      existing_value = str(df_existing_customer_original.loc[row, new_column_header]) if not pd.isna(df_existing_customer_original.loc[row, new_column_header]) else ""
      df_existing_customer_original.loc[row, new_column_header]=existing_value + text
      df_existing_customer_original.to_excel(existing_customers_xls_path, index=False)







