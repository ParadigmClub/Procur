from app import app

if __name__ == '__main__':
    print("Starting Procur...")
    print("Paradigm ❤️ Souvenir Club")
    print("Procurator @ http://localhost:5001")
    print("Credentials: admin / admin123")
    print("Ctrl + C to kill me ")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
