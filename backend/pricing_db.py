"""
Pricing Database - KES (Kenyan Shillings)
Standard market rates for Nairobi/Kenya private hospitals
"""
 
PRICING_DATABASE = {
    # Consultations
    'consultation':              {'min': 500,   'standard': 1200,  'max': 3000},
    'general consultation':      {'min': 500,   'standard': 1200,  'max': 3000},
    'doctor consultation':       {'min': 500,   'standard': 1200,  'max': 3000},
    'specialist consultation':   {'min': 2000,  'standard': 4000,  'max': 8000},
    'follow up':                 {'min': 300,   'standard': 800,   'max': 2000},
    'follow-up':                 {'min': 300,   'standard': 800,   'max': 2000},
    'follow up consultation':    {'min': 300,   'standard': 800,   'max': 2000},
 
    # Imaging
    'x-ray':                     {'min': 1500,  'standard': 2500,  'max': 5000},
    'x ray':                     {'min': 1500,  'standard': 2500,  'max': 5000},
    'xray':                      {'min': 1500,  'standard': 2500,  'max': 5000},
    'chest x-ray':               {'min': 1500,  'standard': 2500,  'max': 5000},
    'mri scan':                  {'min': 8000,  'standard': 15000, 'max': 25000},
    'mri':                       {'min': 8000,  'standard': 15000, 'max': 25000},
    'ct scan':                   {'min': 6000,  'standard': 12000, 'max': 20000},
    'cat scan':                  {'min': 6000,  'standard': 12000, 'max': 20000},
    'computed tomography':       {'min': 6000,  'standard': 12000, 'max': 20000},
    'ultrasound':                {'min': 2000,  'standard': 4000,  'max': 8000},
    'sonography':                {'min': 2000,  'standard': 4000,  'max': 8000},
    'usg':                       {'min': 2000,  'standard': 4000,  'max': 8000},
 
    # Lab Tests
    'blood test':                {'min': 500,   'standard': 1200,  'max': 2500},
    'blood work':                {'min': 500,   'standard': 1200,  'max': 2500},
    'lab test':                  {'min': 500,   'standard': 1200,  'max': 2500},
    'complete blood count':      {'min': 800,   'standard': 1500,  'max': 3000},
    'cbc':                       {'min': 800,   'standard': 1500,  'max': 3000},
    'urine test':                {'min': 400,   'standard': 900,   'max': 1800},
    'urinalysis':                {'min': 400,   'standard': 900,   'max': 1800},
    'lab culture test':          {'min': 1500,  'standard': 3000,  'max': 6000},
    'malaria test':              {'min': 300,   'standard': 700,   'max': 1500},
    'hiv test':                  {'min': 500,   'standard': 1000,  'max': 2000},
    'blood sugar':               {'min': 200,   'standard': 500,   'max': 1000},
 
    # Cardiology
    'ecg':                       {'min': 800,   'standard': 1500,  'max': 3000},
    'ekg':                       {'min': 800,   'standard': 1500,  'max': 3000},
    'electrocardiogram':         {'min': 800,   'standard': 1500,  'max': 3000},
    'echo':                      {'min': 5000,  'standard': 8000,  'max': 15000},
    'echocardiogram':            {'min': 5000,  'standard': 8000,  'max': 15000},
 
    # Procedures
    'injection':                 {'min': 200,   'standard': 500,   'max': 1500},
    'iv drip':                   {'min': 800,   'standard': 1800,  'max': 4000},
    'iv drip administration':    {'min': 800,   'standard': 1800,  'max': 4000},
    'dressing':                  {'min': 300,   'standard': 700,   'max': 1500},
    'wound dressing':            {'min': 300,   'standard': 700,   'max': 1500},
    'suture':                    {'min': 1500,  'standard': 3000,  'max': 6000},
    'stitches':                  {'min': 1500,  'standard': 3000,  'max': 6000},
 
    # Therapy
    'physiotherapy':             {'min': 1000,  'standard': 2500,  'max': 5000},
    'physiotherapy session':     {'min': 1000,  'standard': 2500,  'max': 5000},
    'physical therapy':          {'min': 1000,  'standard': 2500,  'max': 5000},
 
    # Dental
    'dental filling':            {'min': 2000,  'standard': 4000,  'max': 8000},
    'dental checkup':            {'min': 1000,  'standard': 2500,  'max': 5000},
    'dental cleaning':           {'min': 1500,  'standard': 3000,  'max': 6000},
    'teeth cleaning':            {'min': 1500,  'standard': 3000,  'max': 6000},
    'scaling':                   {'min': 1500,  'standard': 3000,  'max': 6000},
    'tooth extraction':          {'min': 2000,  'standard': 4500,  'max': 9000},
 
    # Vaccination
    'vaccination':               {'min': 500,   'standard': 1500,  'max': 5000},
    'vaccine':                   {'min': 500,   'standard': 1500,  'max': 5000},
    'immunization':              {'min': 500,   'standard': 1500,  'max': 5000},
 
    # Admin
    'admission fee':             {'min': 2000,  'standard': 5000,  'max': 10000},
    'registration':              {'min': 200,   'standard': 500,   'max': 1000},
    'registration fee':          {'min': 200,   'standard': 500,   'max': 1000},
 
    # Pharmacy (common meds)
    'medication':                {'min': 150,   'standard': 500,   'max': 3000},
    'medicine':                  {'min': 150,   'standard': 500,   'max': 3000},
    'pharmacy':                  {'min': 150,   'standard': 500,   'max': 3000},
    'amoxicillin':               {'min': 300,   'standard': 700,   'max': 1500},
    'paracetamol':               {'min': 50,    'standard': 150,   'max': 400},
    'specialist referral fee':   {'min': 500,   'standard': 1500,  'max': 3000},
}
 
CURRENCY = "KES"
HIGH_TOTAL_THRESHOLD = 150000   # flag outpatient bills above KES 150k
LOW_TOTAL_THRESHOLD  = 200      # flag bills below KES 200
 
 
def get_standard_price(procedure_name):
    procedure_lower = procedure_name.lower().strip()
    return PRICING_DATABASE.get(procedure_lower)
 
 
def match_procedure(description, threshold=0.55):
    from difflib import SequenceMatcher
    description_lower = description.lower().strip()
 
    # exact match first
    if description_lower in PRICING_DATABASE:
        return description_lower, PRICING_DATABASE[description_lower]
 
    # substring match
    for procedure, price_data in PRICING_DATABASE.items():
        if procedure in description_lower or description_lower in procedure:
            return procedure, price_data
 
    # fuzzy fallback
    best_match, best_score, best_price = None, 0, None
    for procedure, price_data in PRICING_DATABASE.items():
        score = SequenceMatcher(None, description_lower, procedure).ratio()
        if score > best_score:
            best_score, best_match, best_price = score, procedure, price_data
 
    if best_score >= threshold:
        return best_match, best_price
    return None, None
 
 
# ── Inpatient / Surgical / ICU (added post-hackathon sprint)
 
PRICING_DATABASE.update({
    # Theatre & Surgery
    'surgical theatre fee':      {'min': 15000,  'standard': 35000,  'max': 80000},
    'theatre fee':               {'min': 15000,  'standard': 35000,  'max': 80000},
    'operating theatre':         {'min': 15000,  'standard': 35000,  'max': 80000},
    'anaesthesia':               {'min': 8000,   'standard': 20000,  'max': 45000},
    'anaesthesiologist fee':     {'min': 8000,   'standard': 20000,  'max': 45000},
    'surgeon fee':               {'min': 20000,  'standard': 50000,  'max': 150000},
    'surgical procedure':        {'min': 20000,  'standard': 60000,  'max': 200000},
 
    # ICU / HDU
    'icu admission':             {'min': 15000,  'standard': 35000,  'max': 80000},
    'icu admission - 1 day':     {'min': 15000,  'standard': 35000,  'max': 80000},
    'icu admission - 2 days':    {'min': 30000,  'standard': 70000,  'max': 160000},
    'icu admission - 3 days':    {'min': 45000,  'standard': 105000, 'max': 240000},
    'icu':                       {'min': 15000,  'standard': 35000,  'max': 80000},
    'intensive care unit':       {'min': 15000,  'standard': 35000,  'max': 80000},
    'hdu':                       {'min': 8000,   'standard': 18000,  'max': 40000},
    'high dependency unit':      {'min': 8000,   'standard': 18000,  'max': 40000},
 
    # Ventilator / Life Support
    'ventilator support':        {'min': 5000,   'standard': 12000,  'max': 30000},
    'ventilator support - 6hrs': {'min': 5000,   'standard': 12000,  'max': 30000},
    'mechanical ventilation':    {'min': 5000,   'standard': 12000,  'max': 30000},
    'oxygen therapy':            {'min': 1000,   'standard': 3000,   'max': 8000},
    'nebulisation':              {'min': 500,    'standard': 1200,   'max': 3000},
 
    # Ward / Bed charges
    'ward admission':            {'min': 3000,   'standard': 8000,   'max': 20000},
    'bed charges':               {'min': 3000,   'standard': 8000,   'max': 20000},
    'private ward':              {'min': 8000,   'standard': 18000,  'max': 40000},
    'general ward':              {'min': 2000,   'standard': 5000,   'max': 12000},
    'nursing care':              {'min': 2000,   'standard': 5000,   'max': 15000},
 
    # Emergency
    'emergency consultation':    {'min': 2000,   'standard': 5000,   'max': 12000},
    'emergency fee':             {'min': 2000,   'standard': 5000,   'max': 12000},
    'casualty fee':              {'min': 1500,   'standard': 4000,   'max': 10000},
    'ambulance':                 {'min': 3000,   'standard': 8000,   'max': 20000},
 
    # Maternity
    'normal delivery':           {'min': 20000,  'standard': 50000,  'max': 120000},
    'caesarean section':         {'min': 80000,  'standard': 150000, 'max': 300000},
    'c-section':                 {'min': 80000,  'standard': 150000, 'max': 300000},
    'antenatal':                 {'min': 1000,   'standard': 3000,   'max': 8000},
    'postnatal':                 {'min': 1000,   'standard': 3000,   'max': 8000},
 
    # Specialist procedures
    'endoscopy':                 {'min': 10000,  'standard': 25000,  'max': 60000},
    'colonoscopy':               {'min': 15000,  'standard': 35000,  'max': 80000},
    'biopsy':                    {'min': 5000,   'standard': 12000,  'max': 30000},
    'dialysis':                  {'min': 8000,   'standard': 18000,  'max': 40000},
    'chemotherapy':              {'min': 30000,  'standard': 80000,  'max': 300000},
    'radiotherapy':              {'min': 20000,  'standard': 60000,  'max': 200000},
    'blood transfusion':         {'min': 5000,   'standard': 12000,  'max': 30000},
 
    # Common labs (additional)
    'liver function test':       {'min': 1500,   'standard': 3000,   'max': 6000},
    'lft':                       {'min': 1500,   'standard': 3000,   'max': 6000},
    'renal function test':       {'min': 1500,   'standard': 3000,   'max': 6000},
    'thyroid function test':     {'min': 2000,   'standard': 4000,   'max': 8000},
    'lipid profile':             {'min': 1500,   'standard': 3000,   'max': 6000},
    'hba1c':                     {'min': 1500,   'standard': 3000,   'max': 6000},
    'psa':                       {'min': 2000,   'standard': 4000,   'max': 8000},
    'widal test':                {'min': 500,    'standard': 1200,   'max': 2500},
    'cd4 count':                 {'min': 2000,   'standard': 4500,   'max': 9000},
    'viral load':                {'min': 5000,   'standard': 10000,  'max': 20000},
 
    # Blood counts
    'red blood cell count':      {'min': 800,    'standard': 1500,   'max': 3000},
    'white blood cell count':    {'min': 800,    'standard': 1500,   'max': 3000},
    'white blood cell differential': {'min': 1000, 'standard': 2000, 'max': 4000},
    'platelet count':            {'min': 800,    'standard': 1500,   'max': 3000},
    'haemoglobin measurement':   {'min': 500,    'standard': 1200,   'max': 2500},
    'haematocrit analysis':      {'min': 500,    'standard': 1200,   'max': 2500},
})