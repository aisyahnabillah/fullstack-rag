import { useState } from 'react';
import axios from 'axios';
import { BounceLoader } from 'react-spinners';
import ReactMarkdown from 'react-markdown';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000'  // Changed to local backend
})

const Expander = ({ title, content }) => {
    const [isOpen, setIsOpen] = useState(false);
    return (
        <div className="expander">
            <b onClick={() => setIsOpen(!isOpen)} className="expander-title">{title}</b>
            {isOpen && <p className="expander-content">{content}</p>}
        </div>
    );
};

function QuestionForm() {
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [documents, setDocuments] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setAnswer('');
        setDocuments([]);
        setIsLoading(true);
        
        try {
            console.log("Your question: ", question);
            console.log("Calling backend at ", api.defaults.baseURL);
            const response = await api.post('/chat', { message: question });
            setAnswer(response.data.answer);
            setDocuments(response.data.documents);
        } catch (error) {
            console.error("Error:", error);
            setAnswer("Error: " + error.message);
        } finally {
            setIsLoading(false);
        }
    }

    const handleIndexing = async(e) => {
        e.preventDefault();
        setAnswer('');
        setDocuments([]);
        setIsLoading(true);
        
        try {
            const response = await api.post('/indexing', { message: question });
            setAnswer(response.data.response);
        } catch (error) {
            console.error("Error:", error);
            setAnswer("Error: " + error.message);
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <div className="main-container">
            <form className="form">
                <input 
                    className="form-input" 
                    type="text" 
                    value={question} 
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask a question or enter URL to index"
                />
                <div className="button-container">
                    <button className="form-button" type="submit" onClick={handleSubmit}>Q&A</button>
                    <button className="form-button" type="submit" style={{backgroundColor: 'red'}} onClick={handleIndexing}>Index</button>
                </div>
            </form>
            {isLoading && (
                <div className="loader-container">
                    <BounceLoader color="#3498db" />
                </div>
            )}
            {answer && ( 
            <div className="results-container">
                <div className="results-answer">
                    <h2>Answer:</h2>
                    <ReactMarkdown>{answer}</ReactMarkdown>
                </div>
                {documents.length > 0 && (
                <div className="results-documents">
                    <h2>Documents:</h2>
                    <ul>
                        {documents.map((doc, index) => (
                            <Expander 
                                key={index} 
                                title={`Document ${index + 1} (Score: ${doc.score.toFixed(3)})`}
                                content={doc.metadata.text}
                            />
                        ))}
                    </ul>
                </div>
                )}
            </div>
            )}
        </div>
    );
}

export default QuestionForm;