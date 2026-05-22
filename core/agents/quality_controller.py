from core.apirequest import get_completions

def quality_control_exam(
                exam_text,
                onderwerp,
                blooms,
                niveau,
                subdoelen,
                study_material,
                voorbeeldvragen,
                aantal_vragen,
                apikey
): 
        system = """
Vanaf nu ben jij als ai-bot een strenge quality controller voor de tentamenvragen.
Je controleert de gegenereerde vragen op kwaliteit, inhoudelijke juistheid, aansluiting op leerdoelen/subdoelen, aansluiting op studiemateriaal en de correcte Blooms-niveau.
Je mag geen nieuwe tentamenvragen genereren. Je geeft alleen een oordeel en de correcte feedback. 
"""
        user = f"""
Controleer het onderstaande gegenereerde tentamen.

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

VOORBEELDVRAGEN:
{voorbeeldvragen}

GEGENEREERD TENTAMEN:
{exam_text}

Controleer streng op de volgende punten:
1. Aansluiting op de subdoelen.
2. Aansluiting op het studiemateriaal.
3. Correct Bloom-niveau per vraag.
4. Correct aantal vragen per Bloom-niveau.
5. Duidelijke en toetsbare formulering.
6. Geen dubbele of bijna dubbele vragen die 1:1 zijn.
7. Passend taalgebruik voor het opgegeven niveau.
8. Inhoudelijke juistheid.
9. Goede spreiding over de subdoelen.
10. Geen vragen buiten de opgegeven leer-studiestof.
11. Geen subdoel dat onnodig veel vaker voorkomt dan andere subdoelen.
12. Elk verplicht subdoel moet voldoende vertegenwoordigd zijn.
 
Geef je antwoord exact in één van deze twee formaten.

Als het tentamen voldoet:
STATUS: goedgekeurd
FEEDBACK: geen verdere feedback nodig.

Als het tentamen niet voldoet:
STATUS: afgekeurd
FEEDBACK:
- Beschrijf concreet wat moet worden verbeterd.
- Benoem vraagnummer(s).
- Geef aan welk Bloom-niveau of subdoel niet goed is.
- Geef geen volledig nieuw tentamen.
"""

        completion = get_completions(
                model="gpt-4.1",
                system=system,
                user=user,
                key=apikey
        )

        quality_controller_result = completion[0]
        print("Quality Control Uitgevoerd")
        print(quality_controller_result.encode('utf-8', errors='replace').decode('utf-8')) # encoding fouten negeren

        return quality_controller_result