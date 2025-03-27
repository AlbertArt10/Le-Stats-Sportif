from app import webserver

def main():
    # Test: Verificăm dacă DataIngestor, instanțiat în webserver, încarcă corect CSV-ul 
    #   și afișează primele 5 rânduri.
    ingestor = webserver.data_ingestor
    print("Primele 5 rânduri din DataFrame:")
    print(ingestor.df.head())

if __name__ == "__main__":
    main()
