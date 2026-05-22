from datetime import datetime
from core.utils import load_txt, save_results_to_docx
from core.apirequest import get_completions

def leerdoelen_zijn_onvoldoende(leerdoelen: str) -> bool:
        """
        Deze controleert of de aangeleverde leerdoelen ontbreken of onvoldoende concreet zijn voor het tentamen.
        """
        if not leerdoelen or not leerdoelen.strip():
                return True
        
        leerdoelen_clean = leerdoelen.strip()

        woorden = leerdoelen_clean.split()

        if len(woorden) < 5:
                return True
        
        sleutelwoorden = {
                "leren",
                "kennen",
                "kan",
                "kunnen",
                "begrijpen",
                "hoofdstuk",
                "stof",
                "tentamenstof",
                "verklaren",
                "toepassen",
                "analyseren"
        } 
         
        woorden_lower = set(leerdoelen_clean.lower().replace(",", "").replace(".", "").split())

        if len(woorden_lower) <= 4 and woorden_lower.intersection(sleutelwoorden):
                return True

        return False

def generate_subdoelen(leerdoelen, niveau, onderwerp, apikey):
        """
        Dit is DE Learning Goal Generator Agent. 
        Deze genereert op basis van leerdoelen, niveau en onderwerp. 
        """
        print("DEBUG: Learning Goal Generator Agent wordt momenteel gebruikt")

        system = load_txt("data/prompts/subdoelen_system_prompt.txt").format(
                leerdoelen=leerdoelen,
                niveau=niveau,
                onderwerp=onderwerp
        )
    
        user = load_txt("data/prompts/subdoelen_user_prompt.txt").format(
                niveau=niveau, 
                leerdoelen=leerdoelen,
                onderwerp=onderwerp
        )
    
        completion = get_completions(
                model="gpt-4.1", 
                system=system, 
                user=user, 
                key=apikey
        )

        subdoelen = completion[0]
    
        results_dict = {"Subdoelen": subdoelen}
        
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        save_results_to_docx("data/studymaterial/KWM/Subdoelen_{}.docx".format(timestamp), results_dict)
        
        print("Subdoelen opgeslagen")

        return subdoelen

def run_learning_goal_generator(leerdoelen, niveau, onderwerp, apikey):
        """
        De Learning Goal Generator Agent controleer of de leerdoelen ontbreken of minimaal voldoende concreet zijn. 
        """

        if leerdoelen_zijn_onvoldoende(leerdoelen):
                raise ValueError("Fout: De leerdoelen zijn onvoldoende concreet. Subdoelen kunnen niet worden gegenereerd.")

        return generate_subdoelen(
                leerdoelen=leerdoelen,
                niveau=niveau,
                onderwerp=onderwerp,
                apikey=apikey
        )


