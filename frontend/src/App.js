import logo from './logo.svg';
import './App.css';
import QuestionForm from './QuestionForm';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h1 style={{ fontWeight: 600, margin: "20px 0" }}>
          Ask Me Anything 📚✨
        </h1>
        <p style={{ fontSize: "18px", marginBottom: "20px" }}>
          Your AI-powered research assistant
        </p>
        <QuestionForm />
      </header>
    </div>
  );
}

export default App;
