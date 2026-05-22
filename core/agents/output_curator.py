from core.apirequest import get_completions

def output_curator(
                exam_text,
                onderwerp,
                blooms,
                niveau,
                subdoelen,
                study_material,
                aantal_vragen,
                apikey
):
        system = """
Vanaf nu ben jij als ai-bot een strenge output curator voor de tentamenvragen.
Je voert twee sanity checks uit op de definitieve selectie van tentamenvragen.
Je mag geen nieuwe tentamenvragen genereren. Je geeft alleen een oordeel en concrete feedback.
"""
        user = f"""
Voer de twee onderstaande sanity checks uit op het gegenereerde tentamen.

ONDERWERP:
{onderwerp}

NIVEAU:
{niveau}

GEWENSTE BLOOM-NIVEAUS:
{blooms}

GEWENST AANTAL VRAGEN PER BLOOM-NIVEAU:
{aantal_vragen}

SUBDOELEN:
{subdoelen}

STUDIEMATERIAAL:
{study_material}

GEGENEREERD TENTAMEN:
{exam_text}

Voer de volgende twee sanity checks uit:

SANITY CHECK 1. Moeilijkheidsniveau:
1. Controleer of elke vraag past bij het opgegeven niveau: {niveau}.
2. Controleer of het Bloom-niveau van elke vraag overeenkomt met het gewenste Bloom-niveau.
3. Controleer of het totaal aantal vragen per Bloom-niveau klopt met de gewenste verdeling.

SANITY CHECK 2. Aansluiting bij studiemateriaal:
4. Controleer of elke vraag aantoonbaar terug te vinden is in het studiemateriaal.
5. Controleer of er geen vragen zijn die buiten de opgegeven leerstof vallen.
6. Controleer of de vragen aansluiten bij de opgegeven subdoelen.

Geef je antwoord exact in één van deze twee formaten.

Als beide checks slagen:
STATUS: goedgekeurd
FEEDBACK: geen verdere feedback nodig.

Als één of beide checks niet slagen:
STATUS: afgekeurd
FEEDBACK:
- Benoem welke sanity check niet is geslaagd (check 1, check 2, of beide).
- Benoem vraagnummer(s) die niet voldoen.
- Geef aan wat er concreet mis is per vraag.
- Geef geen volledig nieuw tentamen.
"""

        completion = get_completions(
                model="gpt-4.1",
                system=system,
                user=user,
                key=apikey
        )

        output_curator_result = completion[0]
        print("Output Curator Uitgevoerd")
        print(output_curator_result.encode('utf-8', errors='replace').decode('utf-8')) # encoding fouten negeren

        return output_curator_result