from typing import List
import re

class Dienst:
    def __init__(self, raw_data) -> None:
        self.liturgie = raw_data[1]
        self.dienst_data = raw_data[0]
        
    def print(self):
        print("Dienst data: " + self.dienst_data)
        print("")
        print("Liturgie: " + self.liturgie)
        
def fix_liturgie_line_breaks(liturgie):
    lines = []
    
    # Interesting case about liturgie with no line breaks, but only `;`
    max_semicolons = 3
    if liturgie.count(";") > max_semicolons:
        print("Many semicolons")
        print(liturgie)
    
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
    print(headers)
    
    # Liturgien zijn multilines met quotes "" eromheen
    diensten_en_data = data.read().lower().split("\"")
    
    # Maak een Dienst object voor elke dienst
    diensten = []
    # assert(len(diensten_en_data) % 2 == 0)
    for i in range(0, len(diensten_en_data), 2):
        if len(diensten_en_data) < i+2:
            break
        diensten.append(Dienst(diensten_en_data[i:i+2]))
        
    return diensten

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

def main(): 
    diensten = read_in_diensten(file_name="zangdiensten_2023_2024.csv")
    for dienst in diensten:
        dienst.print()
        print("Liederen:")
        print(parse_liederen(dienst.liturgie))
        print()

if __name__ == '__main__':
    main()