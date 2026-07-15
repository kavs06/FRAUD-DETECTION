import ChatBox from "../components/ChatBox";
import "./Chatbot.css";

function Chatbot() {
    return (
        <div className="app-container">

            <header className="app-header">
                <h1>🏥 Healthcare Fraud RAG Chatbot</h1>

                <p>
                    AI-powered assistant for healthcare fraud investigation,
                    provider analysis, and general healthcare information.
                </p>
            </header>

            <main className="chat-container">
                <ChatBox />
            </main>

        </div>
    );
}

export default Chatbot;