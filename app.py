import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template

# Configure the Gemini API using an environment variable that Cloud Run will provide
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

# --- AI Model Initialization ---
model = genai.GenerativeModel('gemini-pro') # Using gemini-pro as a good general-purpose model

# --- Simulated Property Data (For the prototype) ---
# This data is hardcoded for the hackathon. In a real app, it would come from databases.
simulated_properties = {
    "123 Fictional Lane, London SW1A 1AA": {
        "address": "123 Fictional Lane, London SW1A 1AA",
        "type": "Terraced House",
        "beds": 3,
        "price_guide": "£550,000",
        "simulated_risks": [
            "Minor flood risk (low probability, past event nearby)",
            "Approved planning for small extension on neighbouring property",
            "Leasehold property (90 years remaining on lease)",
            "EPC Rating: C (Good)",
            "Local council tax band: D"
        ],
        "simulated_documents": {
            "lease_snippet": "Clause 4.1: The Leaseholder shall pay annual ground rent of £250. Clause 7.2: No structural alterations without Lessor's prior written consent.",
            "planning_excerpt": "Application 2024/00123/EXT: Approved for single-storey rear extension at 125 Fictional Lane."
        }
    },
    "456 Prototype Mews, Manchester M1 1AB": {
        "address": "456 Prototype Mews, Manchester M1 1AB",
        "type": "Detached House",
        "beds": 4,
        "price_guide": "£400,000",
        "simulated_risks": [
            "No significant flood risk identified",
            "No recent planning applications nearby",
            "Freehold property",
            "EPC Rating: B (Very Good)",
            "Local council tax band: C"
        ],
        "simulated_documents": {
            "survey_highlight": "Roof appears in good condition. Damp readings found in utility room (minor, likely condensation).",
            "local_amenity_note": "Within 0.5 miles of 'Outstanding' Ofsted primary school."
        }
    }
}


# --- Routes for the Web App ---

@app.route('/')
def index():
    """Renders the main web page."""
    # This sends the list of simulated property addresses to the HTML page
    property_addresses = list(simulated_properties.keys())
    return render_template('index.html', properties=property_addresses)

@app.route('/health_check', methods=['POST'])
def health_check():
    """
    Simulates a property health check using AI based on selected property.
    The AI generates a summary of risks and details from our simulated data.
    """
    data = request.json
    selected_address = data.get('address')

    if selected_address not in simulated_properties:
        return jsonify({"error": "Property not found"}), 404

    property_data = simulated_properties[selected_address]
    # Format the simulated risks and document snippets into a string for the AI
    risks_str = "\n".join(property_data["simulated_risks"])
    documents_str = ""
    for doc_type, snippet in property_data["simulated_documents"].items():
        documents_str += f"\n{doc_type.replace('_', ' ').title()}: {snippet}"

    # Construct the prompt for the AI to analyze the simulated data
    prompt = (
        f"Analyze the following UK property details and simulated risks for {selected_address}. "
        f"Provide a concise summary of potential concerns for a homebuyer, what they mean, and what to ask about.\n\n"
        f"Property Type: {property_data['type']}\n"
        f"Price Guide: {property_data['price_guide']}\n"
        f"Simulated Risks & Details:\n{risks_str}\n\n"
        f"Simulated Document Snippets:\n{documents_str}\n\n"
        "Focus on key implications for a buyer in the UK property context. Keep it under 200 words."
    )

    try:
        # Debug print: Check if API Key is detected before the call
        print(f"DEBUG_HS_AI: Attempting Gemini call for Health Check. API Key set: {bool(os.getenv('GEMINI_API_KEY'))}")
        # Make the call to the Gemini AI model
        response = model.generate_content(prompt)
        ai_summary = response.text
        return jsonify({
            "address": selected_address,
            "summary": ai_summary,
            "data_used": property_data # Include this for transparency in hackathon demo
        })
    except Exception as e:
        print(f"Error generating AI content: {e}") # This print goes to stderr/stdout
        return jsonify({"error": "Could not generate AI summary. Please try again."}), 500

@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    """
    Handles AI Q&A for UK property.
    The AI answers questions based on its general knowledge (fine-tuned by our prompt).
    """
    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({"error": "No question provided"}), 400

    # This is the prompt for the AI to answer general UK property questions
    prompt = (
        f"You are HomeSense AI, an expert on UK residential property. "
        f"Answer the following question about UK property, conveyancing, or market trends. "
        f"Be concise, informative, and provide practical advice where relevant. "
        f"If the question is beyond typical property scope, state that you focus on property. "
        f"Question: {question}"
    )

    try:
        # Debug print: Check if API Key is detected before the call
        print(f"DEBUG_HS_AI: Attempting Gemini call for Q&A. API Key set: {bool(os.getenv('GEMINI_API_KEY'))}")
        # Make the call to the Gemini AI model
        response = model.generate_content(prompt)
        ai_answer = response.text
        return jsonify({"question": question, "answer": ai_answer})
    except Exception as e:
        print(f"Error generating AI answer: {e}") # This print goes to stderr/stdout
        return jsonify({"error": "Could not get AI answer. Please try again."}), 500

@app.route('/get_valuation', methods=['POST'])
def get_valuation():
    """
    Generates a simulated property valuation estimate using AI.
    """
    data = request.json
    address = data.get('address')
    prop_type = data.get('type')
    beds = data.get('beds')
    condition = data.get('condition')

    if not all([address, prop_type, beds, condition]):
        return jsonify({"error": "Missing valuation details"}), 400

    prompt = (
        f"You are HomeSense AI, an expert UK property valuer. Based on the following simulated details, "
        f"provide a highly realistic property valuation estimate (e.g., '£XYZ,000') and a brief "
        f"justification (max 50 words) for a property with these characteristics:\n\n"
        f"Address/Postcode: {address}\n"
        f"Property Type: {prop_type}\n"
        f"Number of Bedrooms: {beds}\n"
        f"Condition: {condition}\n\n"
        f"Provide the estimate first, then the reasoning. Example: '£450,000. Justification: Recent sales of similar terraced homes in SW1A 1AA support this, accounting for good condition.'"
    )

    try:
        # Debug print: Check if API Key is detected before the call
        print(f"DEBUG_HS_AI: Attempting Gemini call for Valuation. API Key set: {bool(os.getenv('GEMINI_API_KEY'))}")
        response = model.generate_content(prompt)
        ai_response = response.text

        # Attempt to parse the AI's response into estimate and reasoning
        # This is a basic split; more robust parsing might be needed for production
        parts = ai_response.split('Justification:', 1)
        estimate = parts[0].strip()
        reasoning = parts[1].strip() if len(parts) > 1 else "No specific reasoning provided by AI."

        return jsonify({
            "estimate": estimate,
            "reasoning": reasoning
        })
    except Exception as e:
        print(f"Error generating AI valuation: {e}") # This print goes to stderr/stdout
        return jsonify({"error": "Could not generate AI valuation. Please try again."}), 500


if __name__ == '__main__':
    # When running on Cloud Run, Google sets the PORT environment variable.
    # We tell Flask to listen on that port (usually 8080) and on all network interfaces (0.0.0.0).
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
