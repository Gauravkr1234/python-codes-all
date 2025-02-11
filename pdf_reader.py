import streamlit as st
import PyPDF2
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

def extract_text_from_pdf():
    uploaded_file = st.file_uploader("📄 Upload a PDF", type="pdf")
    if uploaded_file:
        try:
            reader = PyPDF2.PdfReader(uploaded_file)
            text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
            st.session_state.uploaded_pdf_text = text
            st.success("✅ PDF uploaded successfully!")
        except Exception as e:
            st.error(f"❌ Error reading PDF: {e}")

def model_llm():
    return ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0,
        groq_api_key="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"
    )

def query_pdf_content(query):
    if "uploaded_pdf_text" not in st.session_state or not st.session_state.uploaded_pdf_text:
        st.warning("⚠️ Please upload a PDF before asking questions!")
        return

    prompt = PromptTemplate.from_template(
        """
        You are a PDF content assistant. The following text is extracted from a PDF document:
        ---
        {pdf_content}
        ---
        Answer the user's query based on the above content. If the answer is not found, reply with 'No information exists.'
        Query: {query}
        """
    )
    llm = model_llm()
    chain = prompt | llm
    response = chain.invoke({"pdf_content": st.session_state.uploaded_pdf_text, "query": query})
    return response.content.strip()

def handle_query(query):
    if "active_conversation" not in st.session_state or not st.session_state.active_conversation:
        st.warning("⚠️ Start a new conversation before asking questions!")
        return

    response = query_pdf_content(query)
    if response:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.conversations[st.session_state.active_conversation]["messages"].append(
            {"query": query, "response": response, "timestamp": timestamp}
        )

def chat_ui():
    # ---- Custom Styling ----
    st.markdown("""
    <style>
    /* Background */
    .main {
        background: linear-gradient(135deg, #1E1E2F, #343a40);
        color: white;
    }
    
    /* Chatbot Header */
    .genome-logo {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        color: #fff;
        background: linear-gradient(to right, #00FF00, #0099FF);
        -webkit-background-clip: text;
        color: transparent;
    }

    /* Chat Message Cards */
    .chat-container {
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        box-shadow: 2px 2px 12px rgba(0,0,0,0.2);
    }

    .user-msg {
        background: #007bff;
        color: white;
        text-align: left;
    }

    .bot-msg {
        background: #28a745;
        color: white;
        text-align: left;
    }

    /* Timestamp Style */
    .timestamp {
        font-size: 12px;
        color: #ccc;
        text-align: right;
    }
    
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="genome-logo">Genome.AI</div>', unsafe_allow_html=True)

    st.title("📝 PDF Query Chatbot")

    # Initialize session states
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    if "active_conversation" not in st.session_state:
        st.session_state.active_conversation = None
    if "uploaded_pdf_text" not in st.session_state:
        st.session_state.uploaded_pdf_text = ""

    # Sidebar Section
    with st.sidebar:
        st.header("📂 Conversations")
        st.write(f"📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        extract_text_from_pdf()

        if st.button("➕ New Chat"):
            conversation_id = f"chat_{len(st.session_state.conversations) + 1}"
            st.session_state.conversations[conversation_id] = {
                "title": f"Chat {len(st.session_state.conversations) + 1}", "messages": [],
                "created_at": datetime.now()
            }
            st.session_state.active_conversation = conversation_id

        for conv_id, conv in st.session_state.conversations.items():
            if st.button(f"💬 {conv['title']}"):
                st.session_state.active_conversation = conv_id

    # Chat Section
    if st.session_state.active_conversation:
        conversation_id = st.session_state.active_conversation
        conversation = st.session_state.conversations[conversation_id]

        user_query = st.text_input("💬 Ask a question:")
        if st.button("🚀 Send") and user_query:
            handle_query(user_query)

        st.subheader(f"🗨️ {conversation['title']}")

        # Display messages as stylish cards
        for msg in conversation["messages"]:
            st.markdown(f"""
            <div class="chat-container user-msg">
                <strong>🧑‍💼 You:</strong> {msg['query']}
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="chat-container bot-msg">
                <strong>🤖 Bot:</strong> {msg['response']}
                <div class="timestamp">🕒 {msg['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("💡 Start a new conversation by clicking '➕ New Chat' or selecting an existing one!")

chat_ui()
