import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Simulador Vocacional", layout="centered")

API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

INSTRUCCIONES_IA = """
sos un simulador educativo de orientación vocacional y vinculos familiares.
Tu objetivo es crear situaciones hipoteticas realistas donde el usuario asume el rol de un hijo/a hacen preguntas abiertas; ofrecen apoyo sin imponer y ayudan a explorar opciones sin presionar.

Reglas de comportamiento según el perfil elegido:
1. P.A (Padres acompañantes): escuchan activamente, validan las emociones e intereses del hijo, hacen preguntas abiertas, ofrecen apoyo sin imponer y ayudan a explorar opciones sin presionar.
 2. P.E( Padres estrictos): exigen estabilidad económica inmediata o prestigio social, desestiman carreras artísticas, humanisticas o no tradicionales, comparan con otros, imponen mandatos familiares y usan frases autoritarias("de eso te vas a morir de hambre", "en esta familia se estudia tal cosa").

 Variedad vocacional: En cada situacion debes ofrecer muchas opciones. Incluí carreras universitarias tradicionales (Medicina, Abogacia, Ingenieria, etc), carreras modernas, tecnicaturas/terciarios, oficios/trabajos).

 Formato al generar situacion:
 _ Escribí en segunda persona ("Eatas em la mesa..."; "Tu papá te mira y te dice/mamá te mira y te dice ...").
 _Que sea inmersivo, breve (1 o 2 párrafos ) y termine conuna frase directa de los padres esperando respuesta.
"""

if "situacion" not in st.session_state:
    st.session_state.situacion = ""
if "perfil" not in st.session_state:  
    st.session_state.perfil= "P.A (Padres Acompañantes)"
if "respuesta_padres" not in st.session_state:
    st.session_state.respuesta_padres = ""


def generar_escenario(tipo_padre):
  st.session_state.respuesta_padres = ""
  prompt = f"Generá una situacion hipotetica nueva donde el usuario es el hijo/a hablando su futuro vocacional o laboral cons sus {tipo_padre}. Elegí una carrera universitaria, terciaria o trabajo al azar que sea disntinto a los mas obvios."

  with st.spinner("Creando situacón..."):
    res = client.models.generate_content(
        model = "gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=INSTRUCCIONES_IA,
            temperature=0.9,
        ),
    )
    st.session_state.situacion = res.text

st.markdown("### Decidiendo mi futuro")

opcion = st.radio(
     "1 Elegí el tipo de padres:",
     ["P.A ( Padres Acompañantes)", "P.E (Padres Estrictos)"],
     horizontal=True
 )
st.session_state.perfil = opcion

if st.button("Generar situación", type="primary", use_container_width=True):
   generar_escenario(st.session_state.perfil)
            
st.divider()

st.markdown("#### Situacion:")
if st.session_state.situacion:
   st.info(st.session_state.situacion)
else:
   st.write("Toca el botón para generar una situacion...")

st.markdown("#### Punto de vista :")
punto_de_vista = st.text_area(
     label="Escribí que responderías como hijo/a:",
     placeholder="Ej: Les diría que estuve averiguando sobre las salida laboral de esat carrera y...",
     height=130,
 )

if st.button("Enviar mi punto de vista ", use_container_width=True):
   if not st.session_state.situacion:
     st.warning("Primero toca generar situación' arriba.")
   elif not punto_de_vista.strip():
     st.warning("Escribí tu punto de vista en el cuadro antes de enviarlo.")
   else: 
     with st.spinner("Los padres están reaccionando..."):
       prompt_reaccion = f"""
             Contexto previo: El usuario tiene {st.session_state.perfil}.
             Situación planteada: { st.session_state.situacion}
             Respuesta del hijo/a (usuario): "{punto_de_vista}"

             Continua la escena mostrando como reaccioan estos padres según su perfil ({st.session_state.perfil}) ante lo que dijo su hijo/a, y al final agregará una breve reflexion educativa (2 líneas) sobre como influye este tipo de crianza en la eleccion vocacional.
             """
                              
       res_final = client.models.generate_content(
           model = "gemini-3.5-flash-lite",
           contents=prompt_reaccion,
           config=types.GenerateContentConfig(
               system_instruction=INSTRUCCIONES_IA
           ),   
       )
       st.session_state.respuesta_padres = res_final.text

if st.session_state.respuesta_padres:
  st.markdown("#### Reacción de los padres:")
  st.success(st.session_state.respuesta_padres)
              
