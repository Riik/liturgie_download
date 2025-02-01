# This is still a WIP, needs some refactoring. 

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

system_prompt = """
De gebruiker deelt een beschrijving van een kerkdienst. Vind die liederen, psalmen en gezangen in de Liturgie als een lijst. 
Antwoord alleen met deze lijst. Antwoord altijd in het Nederlands. Antwoord in een consistente opmaak. 
Als je niks vindt, antwoord dan met een lege lijst. Antwoord altijd met alleen een lijst.
"""

example = """Hemelvaart: eens geen volk, nu Gods volk! \n'
De kerkdienst wordt gehouden in de Immanuelkerk en wordt ook uitgezonden via 
Youtube.\n
Klik \n
hier\n
 om de dienst van deze week te bekijken.\n
Liturgie\n
Opening van de dienst: welkom!\n
 Openingspsalm: Psalm 47 (DNP)\n
 Wat is Hemelvaart? Introductie op de viering van Hemelvaart\n
 Lied: Al heeft Hij ons verlaten (NLB 663)\n
Kinderkunst Kidz678\n
Gebed voor de opening van het Woord\n
 Eerste lezing: Lucas 24,36-53\n
 Lied: Thy hand o God has guided (vers 1)\n
 Tweede lezing: 1 Petrus 1,22 - 2,10\n
 Lied: Thy hand o God has guided (vers 3)\n
 Preek\n
 Psalm 118:1,2,6,7 (DNP)\xa0\n
Collecte en voorbeden\n
 Slotlied: NLB 675:1\n
 Zegen (en gezongen amen)\n
"""

example_2 = """
De kerkdienst wordt gehouden in de Immanuelkerk en wordt ook uitgezonden via 
Youtube\n
Klik \n
hier\n
 om de dienst van deze week te bekijken\n
Liturgie\n
Votum en groet – Sela\n
 Welkom\n
 Belijdenis\n
 Lied Pvn 16 (Ik val niet uit zijn hand)\n
 Kort intro\n
 Gebed\n
 Lied Pvn 130 (Uit de diepten)\n
 Bijbellezing Gen. 37 : 2b – 11\n
 Lied OPW 733 (Tienduizend redenen)\n
 Preek\n
 Lied OPW 599 (Kom tot de Vader)\n
 Mededelingen / collecte\n
 Voorbede\n
 Lied OPW 595 (Licht van de wereld)\n
 Zegen\n
Rooster\n
 Houd me op de hoogte\n
\xa0\xa0Delen\n
\xa0\xa0Tweeten\n
\xa0\xa0LinkedIn\n
\xa0\xa0E-mail\n
 Opslaan in mijn agenda\n
 Outlook\n
 Google Kalender\n
 iCalendar
 """

example_response_2 = """\
Votum en groet - Sela
Psalmen voor Nu 16 (Ik val niet uit zijn hand)
Psalmen voor Nu 130 (Uit de diepten)
Opwekking 733 (Tienduizend redenen)
Opwekking 599 (Licht van de wereld)
"""

example_response = """\
Psalm 47 (DNP)
Al heeft Hij ons verlaten (NLB 663)
Thy hand o God has guided (vers 1 en 3)
Psalm 118:1,2,6,7 (DNP)
NLB 675:1
"""

def extract_songs_from_liturgy(text):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": example},
            {"role": "assistant", "content": example_response},
            {"role": "user", "content": example_2},
            {"role": "assistant", "content": example_response_2},
            {"role": "user", "content": text},
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content

if RERUN_OPENAI:
    responses = {}
    for index, row in tqdm(df.iterrows()):
        responses[row.file] = extract_songs_from_liturgy(row.content)

    with open("api_responses.json", 'w') as o:
        o.write(json.dumps(responses))

with open("api_responses.json", 'r') as f:
    responses = json.loads(f.read())


ai_summaries = pd.DataFrame([(key, value) for key, value in responses.items()], columns=["file", "songs_ai"])
combined = ai_summaries.merge(df)