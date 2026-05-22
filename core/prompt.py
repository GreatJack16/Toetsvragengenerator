from core.utils import load_txt, save_results_to_pdf, save_results_to_docx
from core.apirequest import get_completions
from core.agents.quality_controller import quality_control_exam
from core.agents.output_curator import output_curator
from core.helper.answer_shuffler import randomise_exam
from core.apikey import apikey
from datetime import datetime

def generate_exam(onderwerp, blooms, niveau, subdoelen, study_material, voorbeeldvragen, aantal_vragen, apikey, feedback=""):

        system = load_txt("data/prompts/system_prompt.txt").format(
                                                onderwerp=onderwerp, 
                                                      niveau=niveau, 
                                                      subdoelen=subdoelen, 
                                                      study_material=study_material)
        
        user = load_txt("data/prompts/user_prompt.txt").format(
                                                  subdoelen=subdoelen,
                                                  voorbeeldvragen=voorbeeldvragen,
                                                  blooms=blooms,
                                                  aantal_vragen=aantal_vragen,
                                                  study_material=study_material)
        
        # Als QC feedback heeft gegeven, voeg de feedback toe aan de prompt, zodat AI de verbeterde versie van het tentamen maakt.
        if feedback:
                        user += f"""

        FEEDBACK VAN DE QUALITY CONTROLLER:
        {feedback}

        Maak een verbeterde versie van het tentamen waarin de feedback van de Quality Controller Agent is verwerkt.
        Lever a.u.b. alleen het volledige EN verbeterde tentamen in.
        """

        completion = get_completions(model="gpt-4.1", system=system, user=user, key=apikey)
        exam_text = completion[0]

        timestamp = datetime.now().strftime("%Y-%m-%d")
        results_dict = {"Tentamen: {}".format(onderwerp): exam_text}
        save_results_to_docx("data/outputs/tentamen_vragen_{}.docx".format(timestamp), results_dict)

        print("Tentamen is opgeslagen")
        return exam_text

def generate_exam_with_quality_control(onderwerp, blooms, niveau, subdoelen, study_material, voorbeeldvragen, aantal_vragen, apikey, max_iterations=3):
        feedback = ""
        last_exam_text = ""

        for iteratie in range(max_iterations):
                print(f"Generatie ronde {iteratie + 1} van {max_iterations}")

                exam_text = generate_exam(
                        onderwerp=onderwerp,
                        blooms=blooms,
                        niveau=niveau,
                        subdoelen=subdoelen,
                        study_material=study_material,
                        voorbeeldvragen=voorbeeldvragen,
                        aantal_vragen=aantal_vragen,
                        apikey=apikey,
                        feedback=feedback
                ) 

                last_exam_text = exam_text

                quality_controller_resultaat = quality_control_exam(
                        exam_text=exam_text,
                        onderwerp=onderwerp,
                        blooms=blooms,
                        niveau=niveau,
                        subdoelen=subdoelen,
                        study_material=study_material,
                        voorbeeldvragen=voorbeeldvragen,
                        aantal_vragen=aantal_vragen,
                        apikey=apikey
                ) 

                result_lower = quality_controller_resultaat.lower()

                if "status: goedgekeurd" in result_lower:
                        print("Tentamen goedgekeurd door Quality Controller Agent")
                        return randomise_exam(exam_text)
                
                elif "status: afgekeurd" in result_lower:
                        feedback = quality_controller_resultaat
                        print("Tentamen afgekeurd. Feedback wordt opnieuw meegegeven aan generate_exam.")
                else: 
                        feedback=f"""
                        De Quality Controller gaf geen geldig statusformat terug.
                        Originele output van QC:
                        {quality_controller_resultaat}
                        Verbeter dus het tentamen alsnog op:
                        - aansluiting op subdoelen
                        - aansluiting op studiemateriaal
                        - Bloom-niveaus
                        - aantal vragen
                        - inhoudelijke juistheid
                        - duidelijke formulering
                        """ 
                        print("Quality controller gaf geen herkenbare of juiste status terug.")

        print("Maximum aantal quality-controller rondes bereikt (3).")
        return randomise_exam(last_exam_text)


def generate_exam_with_curator_loop(onderwerp, blooms, niveau, subdoelen, study_material, voorbeeldvragen, aantal_vragen, apikey, max_curator_iterations=2):
    
    exam_text = generate_exam_with_quality_control(
        onderwerp=onderwerp,
        blooms=blooms,
        niveau=niveau,
        subdoelen=subdoelen,
        study_material=study_material,
        voorbeeldvragen=voorbeeldvragen,
        aantal_vragen=aantal_vragen,
        apikey=apikey
    )

    # curator-loop 
    curator_result = ""

    for iteratie in range(max_curator_iterations):
        print(f"Curator ronde {iteratie + 1} van {max_curator_iterations}")

        curator_result = output_curator(
            exam_text=exam_text,
            onderwerp=onderwerp,
            blooms=blooms,
            niveau=niveau,
            subdoelen=subdoelen,
            study_material=study_material,
            aantal_vragen=aantal_vragen,
            apikey=apikey
        )

        result_lower = curator_result.lower()

        if "status: goedgekeurd" in result_lower:
            print("Tentamen goedgekeurd door Output Curator.")
            return exam_text, curator_result

        elif "status: afgekeurd" in result_lower:
            print(f"Tentamen afgekeurd door curator. Feedback wordt teruggekoppeld.")
            exam_text = generate_exam(
                onderwerp=onderwerp,
                blooms=blooms,
                niveau=niveau,
                subdoelen=subdoelen,
                study_material=study_material,
                voorbeeldvragen=voorbeeldvragen,
                aantal_vragen=aantal_vragen,
                apikey=apikey,
                feedback=curator_result  
            )

        else:
            print("Curator gaf geen herkenbare of juiste status terug.")
            break

    print("Maximum aantal curator-rondes bereikt.")
    return exam_text, curator_result


# niet relevant voor nu 
# def extract_from_testscheme(sheet1, sheet2, selection, key=apikey):
#         system = f"""Je bent een behulpzame en nauwkeurige assistent. Het is jouw taak om informatie op te zoeken in een toetsmatrijs. 
        
#         De toetsmatrijs is een Excel-bestand ingeladen als pandas bestand met daarin leerdoelen, subdoelen, het aantal vragen per leerdoel en de bijbehorende Bloom's niveau's.
#         Je krijgt een onderwerp en je zoekt in de toetsmatrijs de bijbehorende subdoelen en aantal vragen per Bloom's niveau op.
#         De subdoelen van een leerdoel kan je in het tweede tabblad (sheet2) vinden, wat aangeeft waar de leerdoelen en subdoelen vandaan komen (een Zelfstudieopdracht (ZSO), Hoorcollege (HC)).

#         Je doet het volgende:
#         1. Zoek in tabblad 1 (sheet1) naar het onderwerp {selection}.
#         2. Noteer hoeveel vragen er zijn per Bloom's niveau voor de rijen van {selection}. (Onthouden, Begrijpen, Toepassen).
#         3. Zoek in tabblad 2 (sheet2) naar de subdoelen behorende bij het onderwerp {selection}. Negeer spelfouten of kleine verschillen in punctuatie.
#         4. Koppel de subdoelen aan de Bloom's niveaus op basis van het aantal vragen per niveau.  Bijvoorbeeld: "ZSO: Zuur base" heeft 2 vragen op niveau Onthouden, dus koppel daar 2 subdoelen aan.
#         5. Geef de output in JSON-formaat met de volgende velden: subdoel, blooms, aantal_vragen.

#         Algemene richtlijnen:
#         - Maak alleen het totaal aantal vragen zoals aangegeven
#         - Neem het subdoel PRECIES over zoals in de toetsmatrijs
#         - Als er minder vragen zijn dan aantal subdoelen, kies dan willekeurig subdoelen om te koppelen.

#         """

#         user = f"""Hier is de toetsmatrijs, tabblad 1: {sheet1}, tabblad 2:{sheet2}.
#         Geef de output als een JSON-lijst, zoals:
#         [
#          {{
#            "subdoel": "voorbeeld subdoel",
#            "blooms": "Onthouden",
#            "aantal_vragen": 1
#          }}        
#         ]"""

#         completion = get_completions(model="gpt-4.1", temperature=0.5, system=system, user=user, key=apikey)
#         print(completion[0])
#         subdoelen = json.loads(completion[0])
#         print(subdoelen)
#         return subdoelen

        