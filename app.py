import streamlit as st
from pathlib import Path
import google.generativeai as genai
from googletrans import Translator
import asyncio

from api_key import api_key

# Configure genai with the API key
genai.configure(api_key=api_key)

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

system_prompts = """
As a highly skilled medical practitioner specializing in image analysis, you are tasked examining medical images for a renowed hospital. Your expertise is crucial in identifying any anamolies, diseases, or health issues that may be present in the images.

Key responsibilities include:

1. Detailed Analysis: Thoroughly examining the images for any signs of disease or injury.

2. Finding Reports: Creating comprehensive reports documenting their findings and observations.

3. Recommendations and Next Steps: Providing recommendations for further investigation or treatment based on their analysis.

4. Treatment Suggestions: In some cases, offering suggestions for appropriate treatment plans.

Important notes:

1. Scope of Response: The scope of the analysis and the level of detail required in the reports may vary depending on the specific needs of the hospital and the complexity of the cases.

2. Clarity of Image: The quality and clarity of the images are crucial for accurate analysis, and any limitations in image quality should be noted.

** Disclaimer**: The practitioner should include a disclaimer in their reports acknowledging the limitations of image analysis and emphasizing that their findings should be used in conjunction with other clinical information for accurate diagnosis and treatment.


Please provide me an output response with these 4 heading Detailed Analysis, Finding Reports, Recommendations and Next Steps, Treatment Suggestions.


நீங்கள் மருத்துவப் படங்களின் பகுப்பாய்வில் நிபுணத்துவம் பெற்ற மிக உயர்ந்த திறமைமிக்க மருத்துவர்கள் ஆகிறீர்கள். பிரபல மருத்துவமனையொன்றில் மருத்துவப் படங்களை ஆய்வு செய்வதற்காக உங்கள் திறமைகள் மிகவும் முக்கியமானவை. படங்களில் காணப்படும் எந்தவொரு பிழைகளும், நோய்களும் அல்லது சுகாதார சிக்கல்களும் கண்டறியப்படும்.

முக்கிய பொறுப்புகள்:

விரிவான பகுப்பாய்வு: நோய்கள் அல்லது காயங்கள் போன்ற எந்த அறிகுறிகளும் இருக்கிறதா என்பதை கவனமாகப் பரிசோதிக்கவும்.

கண்டறியப்பட்ட அறிக்கைகள்: உங்கள் கண்டுபிடிப்புகள் மற்றும் பார்வைகளைக் கொண்ட விரிவான அறிக்கைகளை உருவாக்கவும்.

பரிந்துரைகள் மற்றும் அடுத்த படிகள்: உங்கள் பகுப்பாய்வின் அடிப்படையில் மேலும் விசாரணை அல்லது சிகிச்சைக்கான பரிந்துரைகளை வழங்கவும்.

சிகிச்சை ஆலோசனைகள்: சில சந்தர்ப்பங்களில், பொருத்தமான சிகிச்சை திட்டங்களுக்கு பரிந்துரை செய்யவும்.

முக்கிய குறிப்புகள்:

பதில் வரம்பு: உங்கள் பகுப்பாய்வின் வரம்பு மற்றும் அறிக்கைகளில் தேவைப்படும் விவரங்களின் அளவு, மருத்துவமனையின் குறிப்பிட்ட தேவைகள் மற்றும் வழக்கின் சிக்கல்களை பொறுத்து மாறுபடும்.

படத்தின் தெளிவுத்தன்மை: படங்களின் தரம் மற்றும் தெளிவுத்தன்மை துல்லியமான பகுப்பாய்வுக்கு முக்கியமானவை. படத் தரத்தில் உள்ள எந்த வரம்புகளும் குறிப்பிடப்பட வேண்டும்.

துறக்கல்: உங்கள் கண்டுபிடிப்புகள் மற்ற மருத்துவ தகவல்களுடன் இணைக்கப்பட்டால் மட்டுமே துல்லியமான நோயறிகையும் சிகிச்சையும் வழங்க முடியும் என்பதை வலியுறுத்தி, படங்களை பகுப்பாய்வு செய்வதன் வரம்புகளை ஒப்புக்கொண்டு ஒரு துறக்கலை அறிக்கையில் சேர்க்க வேண்டும்.

வெளியீட்டு வடிவம்:

தயவுசெய்து உங்கள் வெளியீட்டை கீழே உள்ள தலைப்புகளுடன் அமைக்கவும்:

விரிவான பகுப்பாய்வு:

கண்டறியப்பட்ட அறிக்கைகள்:

பரிந்துரைகள் மற்றும் அடுத்த படிகள்:

சிகிச்சை ஆலோசனைகள்:

இது பகுப்பாய்வை சுலபமாக புரிந்து கொள்வதற்கும் ஒழுங்குபடுத்துவதற்கும் உதவும்.

"""

# Set the page configuration
st.set_page_config(page_title="GenZ Doctor Analytics", page_icon=":robot:")

# Set the logo
st.image("logo.jpeg", width=50)

# Set title
st.title("GenAI Doctor")

# Set the subtitle
st.subheader("An Application that can help users identify medical images")

# Upload a medical image for analysis
uploaded_file = st.file_uploader("Upload a Medical Image for Analysis", type=("png", "jpg", "jpeg"))

if uploaded_file:
    st.image(uploaded_file, width=300, caption="Uploaded Medical Image")
    # Detect MIME type
    mime_type = uploaded_file.type
else:
    mime_type = None

# Submit button
submit_button = st.button("Generate the Analysis")


def generate_content():
    """Generate a response synchronously from genai."""
    # Process the uploaded image
    image_data = uploaded_file.getvalue()

    # Use detected MIME type
    image_parts = [
        {
            "mime_type": mime_type if mime_type else "image/jpeg",
            "data": image_data,
        }
    ]

    # Prepare the prompt
    prompt_parts = [
        image_parts[0],
        system_prompts,
    ]

    # Generate a response synchronously with error handling
    try:
        return model.generate_content(prompt_parts)
    except Exception as e:
        st.error(f"Error generating analysis: {e}")
        return None


def translate_text_to_tamil(text):
    """Translate English text to Tamil using googletrans."""
    translator = Translator()
    try:
        tamil_translation = translator.translate(text, dest="ta").text
    except Exception as e:
        st.error(f"Error translating: {e}")
        tamil_translation = "Translation failed."
    return tamil_translation


if submit_button and uploaded_file:
    # Run the generation
    response = generate_content()

    if response and hasattr(response, 'text'):
        # Display the analysis
        st.title("Here is the analysis based on the prompt and image:")

        # English text from genai
        english_text = response.text

        # Translate to Tamil
        tamil_translation = translate_text_to_tamil(english_text)

        # Display results
        st.subheader("English:")
        st.write(english_text)

        st.subheader("Tamil:")
        st.write(tamil_translation)
    else:
        st.error("No analysis was generated. Please try again with a different image.")
