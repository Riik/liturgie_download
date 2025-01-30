from typing import List

class Dienst:
    def __init__(self, raw_data) -> None:
        self.liturgie = raw_data[1]
        self.dienst_data = raw_data[0]
        
    def print(self):
        print("Dienst data: " + self.dienst_data)
        print("")
        print("Liturgie: " + self.liturgie)

def read_in_diensten(file_name):
    data = open(file_name, "r")
    headers = data.readline().strip("\n").split(",")
    print(headers)
    
    # Liturgien zijn multilines met quotes "" eromheen
    diensten_en_data = data.read().split("\"")
    
    # Maak een Dienst object voor elke dienst
    diensten = []
    # assert(len(diensten_en_data) % 2 == 0)
    for i in range(0, len(diensten_en_data), 2):
        if len(diensten_en_data) < i+2:
            break
        diensten.append(Dienst(diensten_en_data[i:i+2]))
        
    return diensten

# TODO: check voor liederen van meerdere regels
def parse_liederen(liturgie: str) -> List[str]:
    # Parse alle regels 1 voor 1, houd alleen degene met een lied erin
    liederen = [lied for lied in [parse_lied(x) for x in liturgie.split("\n")] if lied != None]
    return liederen

# Patterns:
# Indent/Niets + Lied/Slotlied/Zegenlied/Zingen + Niets/:/.
def parse_lied(lied: str) -> str:
    if "lied" in lied.lower() or "zingen" in lied.lower():
        if ":" in lied:
            return lied.split(":")[1].strip()
        elif "." in lied:
            return lied.split(".")[1].strip()
        else:
            return lied.strip()
    return None

def test_parse_lied():
    assert(parse_liederen("Opw 585") == ["Opw 585"])
    assert(parse_liederen("Lied: Opw 585") == ["Opw 585"])
    assert(parse_liederen("Lied. Opw 585") == ["Opw 585"])
    
    # Moet leeg zijn
    assert(parse_liederen("De kerkdienst wordt gehouden in de Immanuelkerk en wordt ook uitgezonden via Youtube\nKlik \nhier\n om de dienst van deze week te bekijken") 
           == [])

def main():
    diensten = read_in_diensten(file_name="zangdiensten_2023_2024.csv")
    for dienst in diensten:
        dienst.print()
        print("\n")

if __name__ == '__main__':
    main()