import requests
import json

# API Endpoints
SEARCH_URL = "https://proptax.bmcwbgov.in/PropertyTaxOnline/PropertyTax/Online.aspx/SelectAssesseeAdvSearchList"
BILL_URL = "https://proptax.bmcwbgov.in/PropertyTaxOnline/PropertyTax/Online.aspx/SelectPropertyTaxBillPrintReport"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json; charset=utf-8',
    'Referer': 'https://proptax.bmcwbgov.in/PropertyTaxOnline/PropertyTax/Online.aspx',
    'Origin': 'https://proptax.bmcwbgov.in'
}

def get_assessee_number(holding_no):
    """Step 1: Convert Holding Number to Assessee Number"""
    search_filter = {
        "AssesseeNo": "", "HoldingAddress": "", "PostalAddress": "", "CommunicationAddress": "",
        "OwnerName": "", "ContactNumber": "", "HoldingNo": holding_no.strip(), "PlotNumber": "",
        "PropertyZoneID": 1, "WardID": 0, "Block": "",
        "Zone": {
            "AssessmentYearDescription": "2026-2027", "AssessmentYearID": 20, "Code": "BID",
            "Description": "Bidhannagar", "ID": 1, "InActive": False, "InActiveDisplay": "No",
            "LoginHistoryID": 0, "UpdatedDate": ""
        }
    }
    
    payload = {"SearchFilter": json.dumps(search_filter)}
    
    try:
        response = requests.post(SEARCH_URL, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("d") and data["d"] != "[]":
                results = json.loads(data["d"])
                return results[0].get("AssesseeNumber")
    except Exception as e:
        print(f"❌ Search Error: {e}")
    return None

def get_plot_dimensions(assessee_no):
    """Step 2: Fetch detailed bill report and dimensions using Assessee Number"""
    payload = {
        'AssessmentYearID': '20',
        'AssesseeNo': str(assessee_no)
    }
    
    try:
        response = requests.post(BILL_URL, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("d") and data["d"] != "[]":
                # The response is a stringified JSON array containing 4 quarters
                quarters = json.loads(data["d"])
                
                # We can extract baseline property limits from the first quarter entry
                plot = quarters[0]
                
                print("\n" + "="*75)
                print("📋 PROPERTY REGISTRY & DIMENSIONS REPORT")
                print("="*75)
                print(f"Owner Name           : {plot.get('OwnerName')}")
                print(f"Assessee Number      : {plot.get('AssesseeNumber')}")
                print(f"Holding Number       : {plot.get('HoldingNo')}")
                print(f"Block / Plot No      : {plot.get('Block')} / {plot.get('PlotNumber')}")
                print(f"Property Address     : {plot.get('HoldingAddress').strip()}")
                print(f"Property Usage Type  : {plot.get('HoldingType')} ({plot.get('PropertyType')})")
                print(f"Registered Phone     : {plot.get('ContactNumber')}")
                print("-"*75)
                print("💰 VALUATION & TAX DIMENSIONS (ANNUAL)")
                print("-"*75)
                print(f"Annual Valuation (AV): ₹{plot.get('AnnualValuation'):,.2f}")
                print(f"Total Arrear Amount  : ₹{plot.get('ArrearAmount'):,.2f} (Fines: ₹{plot.get('Penalty'):,.2f})")
                print(f"Total Outstanding Due: ₹{plot.get('OutstandingAmount'):,.2f}")
                print(f"Base Holding Tax     : ₹{plot.get('HoldingTax'):,.2f} ({plot.get('HoldingTaxPercentage') * 100:.3f}%)")
                print(f"Garbage Tax          : ₹{plot.get('GarbageTax'):,.2f}")
                print(f"Sewerage Tax         : ₹{plot.get('SewerageTax'):,.2f}")
                print(f"Water Tax            : ₹{plot.get('WaterTax'):,.2f}")
                print("-"*75)
                print("⏳ QUARTERLY BREAKDOWN FOR CURRENT FISCAL YEAR")
                print("-"*75)
                
                for q in quarters:
                    print(f"• {q.get('QuarterDescription')} Quarter ({q.get('QuarterMonthFrom').strip()}-{q.get('QuarterMonthTo').strip()}): "
                          f"Base: ₹{q.get('QuartlyGrossTaxAmount')} | Net Payable: ₹{q.get('QuartlyNetAmountPayble')}")
                          
                print("="*75)
                return
        print("❌ Could not extract details for this Assessee Number.")
    except Exception as e:
        print(f"❌ Dimension Retrieval Error: {e}")

# ================== EXECUTION ==================
if __name__ == "__main__":
    print("=== Bidhannagar Municipal Corporation Deep Search ===")
    holding_input = input("Enter Holding Number (e.g., BJ-00319): ").strip()
    
    if holding_input:
        print(f"\n🔍 Searching for tracking token mapped to {holding_input}...")
        assessee_id = get_assessee_number(holding_input)
        
        if assessee_id:
            print(f"🔗 Found Assessee Token: {assessee_id}. Fetching structural valuation dimensions...")
            get_plot_dimensions(assessee_id)
        else:
            print("❌ No matching active Assessee ID found for this holding setup.")
    else:
        print("Input cannot be blank.")