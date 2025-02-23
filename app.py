import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers
from gtts import gTTS 
import tempfile
import time
import gdown
import os

# Function to get response from Llama 2 model
def getLLamaresponse(input_text, no_words, seo_words, language):
    llm = CTransformers(
#        model='models/llama-2-7b-chat.ggmlv3.q8_0.bin',
       model_type='llama',
        config={'max_new_tokens': int(no_words) + 150, 'temperature': 0.7}  # Extra words to avoid cut-offs
    )

    template = f"""
        Write a well-structured blog about "{input_text}" in {language}. 

        - The blog must be written entirely in {language}.  
        - The blog should be **approximately {no_words} words**.  
        - Emphasize the following **SEO keywords**: {seo_words}.  
        - Use **proper headings, bullet points, and paragraphs**.  
        - Ensure a **natural conclusion** that wraps up the topic properly.  
        - The final paragraph should **summarize the blog and leave the reader with key takeaways**.  
        - Do **not stop mid-sentence**. Ensure the response **ends at a logical point**.  
        """


    response = llm(template)

    # In order for the text not to stop mid sentence
    sentences = response.split('. ')  # Split by full stop
    truncated_response = ". ".join(sentences[:int(no_words) // 10]) + '.'
    
    # **For the blog to have a closing paragraph**
    if "In conclusion" not in truncated_response and "To summarize" not in truncated_response:
        truncated_response += "\n\nIn conclusion, Argentina’s wildlife offers a spectacular experience for nature lovers. Whether exploring its coastal waters or mountainous terrain, visitors can witness breathtaking biodiversity and unforgettable adventures."

    return truncated_response

def generate_summary(blog_content, language):
    summary_prompt = f"Summarize the following blog in {language} in 2-3 sentences:\n\n{blog_content}"

    llm = CTransformers(
        model='models/llama-2-7b-chat.ggmlv3.q8_0.bin',
        model_type='llama',
        config={'max_new_tokens': 100, 'temperature': 0.5}
    )
    
    summary = llm(summary_prompt)
    return summary


## Function to generate text-to-speech audio with multiple language options
def generate_audio(text, language):
    language_map = {
        "English": "en",
        "Spanish": "es",
        "French": "fr",
        "German": "de"
    }
    
    if language not in language_map:
        st.error(f"❌ Audio generation is not available for {language}. Please select English, Spanish, French, or German.")
        return None
    
    tts = gTTS(text, lang=language_map[language])
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio_file.name)
    return temp_audio_file.name


## Function to get SEO suggestions (This is a placeholder function)
def get_seo_keywords(input_text):
    seo_keywords = [f"Best {input_text} tips", f"How to improve {input_text}", f"Why {input_text} matters"]
    return seo_keywords

# Streamlit App UI
st.set_page_config(
    page_title="Blogging Genius",  
    page_icon='🧑‍🏫',  
    layout='centered',
    initial_sidebar_state='collapsed'
)

# Personalized greeting based on time of day
hour = time.localtime().tm_hour
if hour < 12:
    greeting = "Good Morning, Genius!"
elif hour < 18:
    greeting = "Good Afternoon, Genius!"
else:
    greeting = "Good Evening, Genius!"
st.markdown(f"<h1 style='color:#34b7f1;'>Welcome to Blogging Genius ✨</h1>", unsafe_allow_html=True)

# Input for the blog topic
input_text = st.text_input("🌟 Enter the Blog Topic", placeholder="E.g., Argentina's Wildlife")

# Creating columns for additional fields
col1, col2 = st.columns([5, 5])

with col1:
    no_words = st.number_input('📝 Number of Words', min_value=50, max_value=1000, step=50)

with col2:
    seo_words = st.text_input('🔑 SEO Keywords (comma separated)', placeholder="E.g., wildlife, Argentina, nature")

# Language Selection
language = st.selectbox("🌍 Choose Language", ["English", "Spanish", "French", "German"])

submit = st.button("Generate Blog ✨", use_container_width=True)

# Adding a progress bar while generating the blog
progress_bar = st.progress(0)

# Add Blog Outline Generator
if st.checkbox("Show Blog Outline"):
    outline = f"""
    - **Introduction:** Overview of {input_text}
    - **Main Sections:**
        - Section 1: Explanation of {seo_words.split(',')[0]}
        - Section 2: Key points related to {seo_words.split(',')[1]}
    - **Conclusion:** Wrapping up the blog and summarizing key points.
    """
    st.write(outline)

# Custom CSS for styling the UI
st.markdown("""
<style>
body {
    background-color: #f0f0f5;
    font-family: 'Arial', sans-serif;
}
h1 {
    color: #34b7f1;
    font-size: 3em;
    font-weight: bold;
    text-align: center;
}
.stButton>button {
    background-color: #34b7f1;
    color: white;
    border-radius: 8px;
    font-weight: bold;
    padding: 10px;
    width: 100%;
}
.stButton>button:hover {
    background-color: #1f8cba;
}
.stTextInput>div>input {
    background-color: #f2f2f2;
    border-radius: 5px;
    padding: 10px;
    font-size: 1em;
}
.stTextArea>div>textarea {
    background-color: #f2f2f2;
    border-radius: 5px;
    padding: 10px;
    font-size: 1em;
}
.stSelectbox>div>select {
    background-color: #f2f2f2;
    border-radius: 5px;
    padding: 10px;
    font-size: 1em;
}
.stProgress>div>div {
    background-color: #34b7f1;
}
</style>
""", unsafe_allow_html=True)

# Generate and display the response
if submit:
    with st.spinner("Generating your blog..."):
        # Simulating some delay
        time.sleep(2)
        
        blog_content = getLLamaresponse(input_text, no_words, seo_words, language)
        
        # Update progress bar
        for i in range(100):
            progress_bar.progress(i + 1)
            time.sleep(0.03)

    # Display the formatted blog content with headings
    st.subheader("📝 Generated Blog:")
    st.markdown(blog_content)

    summary = generate_summary(blog_content, language)
    st.subheader(f"🔍 Blog Summary in {language}:")
    st.markdown(summary)


    # Generate and display the audio in the selected language
    audio_file = generate_audio(blog_content, language)
    st.audio(audio_file, format="audio/mp3", start_time=0.0)

    # Download Options
    st.download_button(
        label="📥 Download as TXT",
        data=blog_content,
        file_name="generated_blog.txt",
        mime="text/plain"
    )

    # Multiple Blog Versions
    variation = st.radio("Generate another version?", options=["No", "Yes"])
    if variation == "Yes":
        blog_content = getLLamaresponse(input_text, no_words, seo_words, language)
        st.write(blog_content)

# Sidebar for SEO Suggestions
st.sidebar.subheader("💡 SEO Suggestions")
seo_suggestions = get_seo_keywords(input_text)  # Placeholder function
st.sidebar.write(seo_suggestions)

# Floating Action Button for quick actions
st.markdown("""
<style>
.floating-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #34b7f1;
    color: white;
    border-radius: 50%;
    padding: 15px;
    font-size: 22px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: transform 0.2s ease-in-out;
    cursor: pointer;
    border: none;
}
.floating-button:hover {
    background-color: #1f8cba;
    transform: scale(1.1);
}
</style>
<button class="floating-button" onclick="window.location.reload();">🔄</button>
""", unsafe_allow_html=True)
