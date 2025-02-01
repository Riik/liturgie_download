from typing import List
import re

# Script om diensten in te lezen, liederen eruit te parsen en weer in csv
# format op te slaan
# Notes:
# Dit script leest `zangdiensten_2023_2024.csv` in met alle diensten.
# Deze .csv moet je zelf maken en een paar aanpassingen doen aan de data:
#   1. Multi line liturgie wordt ge-exporteerd met "" om de tekst, dus als er nog
#   "" in de tekst staan, dan moet je die eruit halen
#   2. Zorg er ook voor dat in de Datum, Stijl, Bezetting geen , staan
#   want dat is de delimiter voor de csv
# De output is een liederen.csv die de liturgie vervangt voor de liederen


class Dienst:
    def __init__(self, raw_data) -> None:
        self.liturgie = raw_data[1]
        self.dienst_data = raw_data[0].replace("\n", "")
        self.find_liederen()
        
    def print(self):
        print("Dienst data: " + self.dienst_data)
        print("Liederen:")
        for id, lied in enumerate(self.liederen):
            print(str(id+1) + ":" + lied)
        print("")
        print("Liturgie: " + self.liturgie)
        
    def find_liederen(self):
        liederen = parse_liederen(self.liturgie)
        self.liederen = [lied.strip().replace("\n", "").replace(",", "") for lied in liederen]
        
    def write_csv(self, file_name):
        delimiter  = ","
        try:
            with open(file_name, "a") as file:
                file.write(self.dienst_data)
                file.write(delimiter.join(self.liederen) + "\n")
                print(delimiter.join(self.liederen) + "\n")
        except Exception as e:
            print("Error writing to file")
            print(e)
        
def fix_liturgie_line_breaks(liturgie):
    lines = []
    
    # Interesting case about liturgie with no line breaks, but only `;`
    max_semicolons = 3
    if liturgie.count(";") > max_semicolons:
        print("Dienst with many semicolons found")
    
    for line in liturgie.split("\n"):
        # Always add first to to list
        if not lines:
            if not line:
                continue
            lines.append(line)
            continue
            
        # If line ends on a weird character, 
        # or the next line starts on a weird character
        # add it to the previous line
        last_char_last_line = lines[-1].strip()[-1]
        end_separators = [".", ":", ",", "‘"]
        first_char_this_line = line.strip()[0]
        start_separators = [".", ":", ";", ",", "-", "(", "–"]
        if last_char_last_line in end_separators or \
            first_char_this_line in start_separators:
                
            lines[-1] += " " + line
            continue
        
        # Special case when line is only lied, example:
        #   lied 
        #   onze schuilplaats is god
        #   lied 
        #   in ons hart geboren  (sela)
        #   gebed
        if lines[-1].strip().endswith("lied") or lines[-1].strip().endswith("zingen"):
            lines[-1] += " " + line
            continue
        
        if line != "":
            lines.append(line)
    
    return "\n".join(lines)

def read_in_diensten(file_name):
    data = open(file_name, "r")
    headers = data.readline().strip("\n").split(",")
    
    # Liturgien zijn multilines met quotes "" eromheen
    diensten_en_data = data.read().lower().split("\"")
    
    # Maak een Dienst object voor elke dienst
    diensten = []
    # assert(len(diensten_en_data) % 2 == 0)
    for i in range(0, len(diensten_en_data), 2):
        if len(diensten_en_data) < i+2:
            break
        diensten.append(Dienst(diensten_en_data[i:i+2]))
        
    return diensten, headers

def parse_liederen(liturgie: str) -> List[str]:
    regex = r'.*(?:lied|zingen|opw |opw. |opwekking |ps |ps. |psalm |psalmen |psalmproject |nlb |lb: |gezang |tijdens |couplet).*\n'
    # regex = r".*(?:lied).*"
    preprocessed_liturgie = fix_liturgie_line_breaks(liturgie.lower())
    return re.findall(regex, preprocessed_liturgie)

def test_parse_full_liturgie():
    assert(len(parse_liederen("Liturgie: welkom, votum & groet\n\
opwekking 464  \n\
wees stil voor het aangezicht van god\n\
leefregel\n\
opwekking 876 \n\
voor altijd heilig\n\
kindermoment over bidden\n\
gebed\n\
inleiding op de doop\n\
opwekking 599 \n\
kom tot de vader\n\
doopvragen en heilige doop\n\
lied:  zegen voor de kinderen  - sela\n\
bijbellezing: lucas 11: 1-13\n\
preek\n\
opwekking 436 \n\
onze vader\n\
mededelingen\n\
voorbedegebed\n\
collecte: financiële ondersteuning (diaconie)\n\
slotlied:  de kerk van alle tijden  (lev)\n\
zegen")
       ) == 6   )

def write_headers(file_name, headers):
    try:
        with open(file_name, "w") as file:
            file.write(",".join(headers) + "\n")
    except Exception as e:
        print("Error writing to file")
        print(e)

def main(): 
    diensten, headers = read_in_diensten(file_name="zangdiensten_2023_2024.csv")
    
    liederen_csv = "liederen.csv"
    headers[-1] = ("Liederen")
    write_headers(liederen_csv, headers)
    for dienst in diensten:
        dienst.write_csv(liederen_csv)
        dienst.print()

if __name__ == '__main__':
    main()