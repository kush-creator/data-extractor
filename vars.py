from os import environ
from dotenv import load_dotenv, find_dotenv
from json import load

load_dotenv(find_dotenv())

AZURE_KEY=environ.get('AZURE_KEY')
ANTHROPIC_API_KEY=environ.get('ANTHROPIC_API_KEY')

PREFILLED = {
    'Yes Bank (Hand Filled)': 'files/yes_bank_hand.pdf',
    'Yes Bank': 'files/yes_bank.pdf',
    'Ujjivan Bank': 'files/ujjivan.pdf',
    'Axis Bank': 'files/axis_bank.pdf',
    'Navi Micro Finance': 'files/navi.pdf',
}

PASSWORDS = [
    ('soham', 'presolvedemo'),
    ('maifounder', 'maifounderdemo123!'),
]

with open('state.json', 'r') as f:
    state = load(f)
    
GLOBAL_UPLOAD_COUNTER = state['counter']

LIMITS = {
    'soham': state['soham'],
    'maifounder': state['maifounder'],
}

preconfig = [
    {'id':0,'text':'Sr. No.','out':''},
    {'id':1,'text':'Disputed amount / Loan Amount','out':''},
    {'id':2,'text':'Full name of Primary borrower','out':''},
    {'id':3,'text':'Email ID of Primary borrower','out':''},
    {'id':4,'text':'Mobile number of Primary borrower','out':''},
    {'id':5,'text':'Complete Address of Primary borrower','out':''},
    {'id':6,'text':'Pincode of Primary borrower','out':''},
    {'id':7,'text':'Nature of Loan (Vehicle Loan, Business Loan etc.) / Purpose','out':''},
    {'id':8,'text':'Agreement Date','out':''},
    {'id':9,'text':'Arbitration Clause Number','out':''},
    {'id':10,'text':'Email IDs of Additional borrowers','out':''},
    {'id':11,'text':'Mobile numbers of Additional borrowers','out':''},
    {'id':12,'text':'Additional borrowers details','out':''},
    {'id':13,'text':'Agreement number','out':''},
    {'id':14,'text':'Date of Section 21 notice','out':''},
    {'id':15,'text':'SOA/FC date','out':''},
    {'id':16,'text':'Address of the property','out':''},
]


